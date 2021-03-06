
import os
import sys

import subprocess
from subprocess import PIPE, STDOUT, Popen

import settings


def get_board_path(prjctName, prjctPath):

    cmd = 'cd ' + settings.escape_string(prjctPath) + ' && git rev-parse --show-toplevel'

    print("")
    print("Getting SCM top level")
    print(cmd)

    stdout, _ = settings.run_cmd(cmd)
    scm_root = stdout

    cmd = 'cd {scm_root} && git ls-tree -r --name-only HEAD | grep -m 1 {prjctName}'.format(
        scm_root=settings.escape_string(scm_root), prjctName=prjctName)

    print("")
    print("Getting board file")
    print(cmd)

    stdout, _ = settings.run_cmd(cmd)

    return settings.escape_string(stdout)


def get_boards(diff1, diff2, prjctName, kicad_project_path, prjctPath):
    '''Given two git artifacts, write out two kicad_pcb files to their respective
    directories (named after the artifact). Returns the date and time of both commits'''

    artifact1 = diff1[:6]
    artifact2 = diff2[:6]

    # Using this to fix the path when there is no subproject
    prj_path = kicad_project_path + '/'
    if kicad_project_path == '.':
        prj_path = ''

    cmd = \
        'cd ' + settings.escape_string(prjctPath) + ' && ' + \
        'git diff --name-only ' + artifact1 + ' ' + artifact2 + ' . | ' + \
        "grep " + prj_path + prjctName

    print("")
    print("Getting boards")
    print(cmd)

    stdout, stderr = settings.run_cmd(cmd)
    changed = stdout

    if changed == '':
        print("\nThere is no difference in .kicad_pcb file in selected commits")
        sys.exit()

    outputDir1 = prjctPath + '/' + settings.plotDir  + '/' + artifact1
    outputDir2 = prjctPath + '/' + settings.plotDir  + '/' + artifact2

    if not os.path.exists(outputDir1):
        os.makedirs(outputDir1)

    if not os.path.exists(outputDir2):
        os.makedirs(outputDir2)

    # gitPath = get_board_path(settings.escape_string(kicad_project_path) + "/" + prjctName, settings.escape_string(prjctPath))
    gitPath = get_board_path(settings.escape_string(prj_path + prjctName), settings.escape_string(prjctPath))

    gitArtifact1 = 'cd ' + settings.escape_string(prjctPath) + ' && ' + \
        'git show ' + artifact1 + ':' + gitPath + ' > ' + \
        settings.escape_string(outputDir1) + '/' + prjctName

    gitArtifact2 = 'cd ' + settings.escape_string(prjctPath) + ' && ' + \
        'git show ' + artifact2 + ':' + gitPath + ' > ' + \
        settings.escape_string(outputDir2) + '/' + prjctName

    print("")
    print("Get artifacts")
    print("gitPath      :", gitPath)
    print("Git artifact1: ",gitArtifact1)
    print("Git artifact2: ",gitArtifact2)

    stdout, stderr = settings.run_cmd(gitArtifact1)
    stdout, stderr = settings.run_cmd(gitArtifact2)

    gitDateTime1 = 'cd ' + settings.escape_string(prjctPath) + ' && git show -s --format="%ci" ' + artifact1
    gitDateTime2 = 'cd ' + settings.escape_string(prjctPath) + ' && git show -s --format="%ci" ' + artifact2

    print("")
    print("Check datetime")
    print(gitDateTime1)
    print(gitDateTime2)

    stdout, stderr = settings.run_cmd(gitDateTime1)
    dateTime1 = stdout
    date1, time1, UTC = dateTime1.split(' ')

    stdout, stderr = settings.run_cmd(gitDateTime2)
    dateTime2 = stdout
    date2, time2, UTC = dateTime2.split(' ')

    time1 = date1 + " " + time1
    time2 = date2 + " " + time2

    return artifact1, artifact2, time1 + " " + time2


def get_artefacts(prjctPath, board_file):
    '''Returns list of artifacts from a directory'''

    cmd = 'cd {prjctPath} && git log --pretty=format:"%h | %s"'.format(prjctPath=prjctPath)

    stdout, _ = settings.run_cmd(cmd)
    artifacts = stdout.splitlines()

    return artifacts


def get_kicad_project_path(prjctPath):
    '''Returns the root folder of the repository'''

    cmd = "cd {prjctPath} && git rev-parse --show-toplevel".format(
        prjctPath=settings.escape_string(prjctPath))

    stdout, _ = settings.run_cmd(cmd)
    repo_root_path = stdout.strip()

    kicad_project_path = os.path.relpath(prjctPath, repo_root_path)

    return repo_root_path, kicad_project_path
