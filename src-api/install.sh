#!/bin/bash

declare -A langMappings=()
while IFS= read -r -d '' key && IFS= read -r -d '' value; do
    langMappings[$key]=$value
done < <(jq -j 'to_entries[] | (.key, "\u0000", .value, "\u0000")' < mappings.json)
availableLangs=${!langMappings[@]}

# echo "Insert the list of languages to download, separated by space (eg. 'en it')."
# echo "Available languages: ${availableLangs[@]}."
# echo "Leave blank to download all the ${#langMappings[@]} languages (50GB of data approximately)."
# read -a selectedLangs
selectedLangs=( "$@" )

declare -a okLangs=()
if [ ! ${#selectedLangs[@]} -eq 0 ]; then
    for l in ${selectedLangs[@]}; do
        if [[ ! ${availableLangs[@]} =~ $l ]]; then
            echo "Lang $l does not exist, ignoring"
            continue
        fi
        okLangs+=($l)
    done
else
    okLangs=${availableLangs[@]}
fi

if [ ${#okLangs[@]} -eq 0 ]; then
    echo "No languages selected, exiting"
    exit 1
fi

mkdir -p models
cd models
echo "Installing languages: ${okLangs[@]}"
for l in ${okLangs[@]}; do
    echo "Installing model for ${langMappings[$l]^}"
    curl --output ./${langMappings[$l]}.tar.gz https://dh.fbk.eu/software/kevlar-models/${langMappings[$l]}.tar.gz
    tar xzf ${langMappings[$l]}.tar.gz
    rm ${langMappings[$l]}.tar.gz
done
cd ..
