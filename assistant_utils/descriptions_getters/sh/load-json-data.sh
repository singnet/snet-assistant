#!/bin/bash
json_data_dir=$1

# Takes the organization id as first argument and outputs knowledge
organization_to_metta() {
    local org="$1"

    for service in $(snet organization list-services ${org} | tail --lines=+3 | cut -f2 -d" "); do
        service_to_metta ${org} ${service}
    done
}

# Takes the organization id as first argument and service as second
# argument and outputs knowledge about that service in json.
service_to_metta() {
    local org="$1"
    local service="$2"

    # Save json metadata of that service in a file
    local metadata_filepath=$json_data_dir/${org}.${service}.json
    snet service print-metadata ${org} ${service} > ${metadata_filepath}
    echo "Collect information about ${org}.${service}"
}

# Set the network to mainnet
snet network mainnet
if  !(([ -d "$json_data_dir" ])); then
 mkdir $json_data_dir 2> /dev/null
fi

for org in $(snet organization list | tail --lines=+2); do
   
    organization_to_metta "${org}" 
done


