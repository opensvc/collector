#!/bin/bash

PATH_SCRIPT="$(cd $(/usr/bin/dirname $(type -p -- $0 || echo $0));pwd)"
PATH_APP="$PATH_SCRIPT/.."
CSS=$PATH_APP/static/css/base.css
PATH_CODE="$PATH_APP/views $PATH_APP/controllers $PATH_APP/static/views $PATH_APP/static/js/osvc $PATH_APP/models"

for cl in $(egrep -o "\.[a-z][a-z_0-9-]*" $CSS | sort -u | uniq)
do
	usage=$(grep -ro $cl $PATH_CODE | wc -l)
	if [ $usage -eq 0 ]
	then
		echo $cl
	fi
done
