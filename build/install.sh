#!/usr/bin/env bash
set -e
args=("$@")

function installTestPythonDependencies {
    pip3 install -r "./requirements.txt"
}

function runPyTest {
    echo "Printing service"
    echo "########################"
    installTestPythonDependencies
    IFS=',' read -ra DASHBOARDS <<< "$DASHBOARD_NAME"
    DASHBOARD=""
    FILEPATH="src/tests/"
    for i in "${DASHBOARDS[@]}";
    do
      if [ $i == "all" ]
    then
      DASHBOARD="$FILEPATH"
      break
    fi
      DASHBOARD+="${FILEPATH}test_${i}.py "
      done
    set +e
    python -m pytest --html=report.html --self-contained-html -s -v -n $THREAD $DASHBOARD
    if [ $? != 0 ]
    then
      set -e
      sendMail
      exit 1
    fi
}

function sendMail {
    echo "Printing Send Mail"
    echo "########################"
    python ./src/utils/mail_handler.py
    echo "------------------------"
    echo "Removing report"
    echo "########################"
    rm -rf report.html
    echo "------------------------"
}

case "$1" in
    apitest) runPyTest;;
    sendmail) sendMail

esac
