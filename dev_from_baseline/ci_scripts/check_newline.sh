#!/bin/bash
set -u

shopt -s globstar

folder_to_scan=$1

exit_code=0

for file in "$folder_to_scan"**
    do
        if [ -f "$file" ]; then
            A="$(printf '\n')"; B="$(tail -c1 "$file")" ; test "$A" = "$B"`` 
            result=$?
            if [ "$result" -ne "0" ]; then 
                echo "$file no newline at the end of file"
                exit_code=1
            fi
        fi
    done

if [ $exit_code -eq 0 ]; then
    # shellcheck disable=SC2028
    echo "All files have \n at the end"
fi
exit $exit_code
