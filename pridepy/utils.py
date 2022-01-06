import sys
import os.path
import json
import pandas as pd
from pridepy import Project
from pridepy.util.api_handling import Util
from pridepy.files import Files

api_base_url = "https://www.ebi.ac.uk/pride/ws/archive/v2/"
api_token = 'eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FhaS5lYmkuYWMudWsvc3AiLCJqdGkiOiJUWVJVLXFnMG1OV1EzbkJLcXp2aGZ3IiwiaWF0IjoxNjQxNDQzOTQ2LCJzdWIiOiJ1c3ItZTkxNzRkZDAtOWU4Yi00OTY4LTg0NjQtM2ExZWRhYWY4NDY3IiwiZW1haWwiOiJhbmlsQGliaW9pbmZvcm1hdGljcy5vcmciLCJuaWNrbmFtZSI6ImFuaWxAaWJpb2luZm9ybWF0aWNzLm9yZyIsIm5hbWUiOiJBbmlsIE1hZHVndW5kdSIsImRvbWFpbnMiOlsic2VsZi5wcmlkZS5zdWJtaXQiXSwiZXhwIjoxNjQxNDQ3NTQ2fQ.HKGd9pjnhwHUvvsuOmnzet9LdJ-SlukcX4_mKXKIDMh618F25tUisGkcyk5V6TuolUR_TPLOGRqj6PKWNaRooD9Iso29yAJ8Hhx2bIsqzM2gTtoO4wWLs-UNQBzT1zF-JM3l7rrAgNd8W_gqdkFVxeQUHGJ3zbdsW5DrVsNDOJdTaL0DvYjldvDGD9zAnVshTDukKWtQsLsaGrSs_fb1EiNQpU9EnvtFTyAW2bAwEMnlGRdv3fQSDdQBgleVBsfPXna7PCsBIq2f15zospJaovog5hrhTtO2LFq8mq6L-Hn2GwE4vuaga6DYVIDxuhEkyWAI5JBH55UNFUf6BjPDBg'


def project_with_keywords(pride_key_words, only_human=True):
    """
    Search the PRIDE projects for keywords and filter by matching `keyword` across the project information
    :param list pride_key_words: File name of the project summary in JSON format
    :param bool only_human: Filter for human or not
    :returns: str file name with matching PRIDE projects
    """
    # pride_key_words = ['cancer', ] #'human', 'cancer', 'phosphorylation'
    pride_keywords = "*%s*" '*'.join(pride_key_words)
    pride_filter_values = {'organisms': 'Homo sapiens (human)'} if only_human else dict()
    pride_filters = ','.join(['%s==%s' % (k,w) for k,w in pride_filter_values.items()])
    if not os.path.exists(os.path.join(os.path.curdir, 'data')):
        os.mkdir(os.path.join(os.path.curdir, 'data'))
    json_fname = os.path.join(os.path.curdir, 'data', "%s_projects.json" % '_'.join(pride_key_words))
    if os.path.exists(json_fname):
        return json_fname
    page_size, date_gap, sort_direction, sort_fields = 100, '', 'DESC', 'submission_date'
    max_pages = int(10000 / page_size)
    p = Project()
    results_all = []
    for page in range(max_pages):
        results = p.search_by_keywords_and_filters(pride_keywords, pride_filters, page_size, page, date_gap, sort_direction, sort_fields)
        results_all.append(results)
        if len(results['_embedded']['compactprojects']) < page_size:
            break
        else:
            sys.stderr.write("+")
    sys.stderr.write(os.linesep)
    with open(json_fname, 'w') as jsout:
        json.dump(results_all, jsout)
    print('Number of studies: {:d}'.format((len(results_all) - 1) * page_size + len(results['_embedded']['compactprojects'])))
    return json_fname


def projects_info(project_fname, keyword=None):
    """
    Summarize the PRIDE projects and filter by matching `keyword` across the project information
    :param str project_fname: File name of the project summary in JSON format
    :param str keyword: String of keyword to filter projects
    :returns: pandas.core.frame.DataFrame with  matching PRIDE projects

    Additional summary
    ------------------
    >>> pd.DataFrame(np.unique(np.concatenate(phospho_proj_info['keywords'].values), return_counts=True), index=['keyword', 'count']).transpose().sort_values('count', ascending=False)
    """
    json_fname = project_fname.replace('.json', ".projects.json")
    prj = Project()
    if os.path.exists(json_fname):
        with open(json_fname, 'rb') as jsin:
            projects_all = json.load(jsin)
    else:
        projects_all = dict()
    keys = ['accession', 'organisms', 'title', 'diseases', 'keywords', 'submissionType', 'labPIs', 'organismParts', 'instruments', 'affiliations', 'submissionDate', 'publicationDate']
    keyfunc = [str, ';'.join, str, ','.join, ';'.join, str, ';'.join, ';'.join, ';'.join, ','.join, str, str]
    with open(project_fname, 'r') as jsin:
        results_all = json.load(jsin)
    projects_ndarray = []
    for rs in results_all:
        for p in rs['_embedded']['compactprojects']:
            if p['accession'] in projects_all:
                prj_json = projects_all[p['accession']]
            else:
                prj_json = prj.get_by_accession(p['accession'])
                projects_all[p['accession']] = prj_json
            project_array = []
            for k in keys:
                v = prj_json[k] if k in prj_json else None
                project_array.append(v)
            projects_ndarray.append(project_array)
    with open(json_fname, 'w') as jsout:
        json.dump(projects_all, jsout)
    proj_info = pd.DataFrame(projects_ndarray, columns=keys)
    if not keyword:
        return proj_info
    return proj_info[(proj_info.apply(lambda x: x.to_json().lower().find(keyword) > -1, axis=1) == True)]


def project_files(accession, category=None, exclude_filetypes=None, exclude_raw=False, only_result=False):
    """
    Get all files list from PRIDE API for a given project_accession
    :param accession: PRIDE accession
    :param category: Sub-category of files to list (eg. SEARCH, RESULT)
    :param exclude_filetypes: Exclude files of certain type (eg. .msf or .pdresult)
    :param exclude_raw: Filter raw files from list
    :param only_result: Return only SEARCH and RESULT files
    :return: file list in JSON format
    """
    request_url = api_base_url + "files/byProject?accession=" + accession
    if category:
        request_url += ",fileCategory.value==%s" % category
    headers = {"Accept": "application/JSON"}
    response = Util.get_api_call(request_url, headers)
    response_json = response.json()
    if exclude_raw:
        rs_no_raw_files = []
        for fl in response_json:
            if fl['fileCategory']['value'] == 'RAW': continue
            if only_result:
                if not fl['fileCategory']['value'] in ('SEARCH', 'RESULT'): continue
            if exclude_filetypes:
                fname = fl['fileName'].lower()
                exclude_filetypes = [exclude_filetypes, ] if isinstance(exclude_filetypes, str) else exclude_filetypes
                for exclude_filetype in exclude_filetypes:
                    if fname.endswith(exclude_filetype) or fname.endswith(exclude_filetype + '.zip') or fname.endswith(exclude_filetype + '.gz'): continue
            rs_no_raw_files.append(fl)
        return rs_no_raw_files
    return response_json


def project_files_download(accession, category=None, exclude_raw=False, only_result=False):
    """
    Get all files list from PRIDE API for a given project_accession
    :param accession: PRIDE accession
    :param category: Sub-category of files to list (eg. SEARCH, RESULT)
    :param exclude_raw: Filter raw files from list
    :param only_result: Return only SEARCH and RESULT files
    :return: file list in JSON format
    """
    prj_folder = os.path.join(os.path.curdir, 'data', accession, '')
    # Skip if the project download folder already present
    if not os.path.exists(prj_folder):
        os.mkdir(prj_folder)
        file_list_json = project_files(accession, category=category, exclude_raw=exclude_raw, only_result=only_result)
        Files.download_files_from_ftp(file_list_json, prj_folder)
