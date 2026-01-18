#!/bin/bash

# Ensure curl is available for auto-detection
if ! command -v curl &> /dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y curl -qq > /dev/null
fi

# 1. Attempt Auto-Detection via IP
echo "Attempting to auto-detect timezone via IP..."
AUTO_TZ=$(curl -s --connect-timeout 5 http://ip-api.com/line?fields=timezone)

if [ -n "$AUTO_TZ" ] && [[ "$AUTO_TZ" == *"/"* ]]; then
    echo "Detected Timezone: $AUTO_TZ"
    read -t 15 -p "Use this timezone? (Y/n): " confirm
    confirm=${confirm:-y} 
    
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        sudo timedatectl set-timezone "$AUTO_TZ"
        echo "Timezone set to $AUTO_TZ."
        echo "The system time is now: $(date)"
        exit 0
    fi
fi

# 2. Loopable Search Feature
while true; do
    echo "-----------------------------------------------"
    echo "Manual Timezone Selection"
    echo "Enter a city/region to filter (e.g., 'America' or 'New_York')"
    echo "Type 'exit' to keep current settings."
    echo "-----------------------------------------------"
    
    read -p "Search: " search_term
    
    # Exit condition
    if [[ "$search_term" == "exit" ]]; then
        echo "Exiting timezone setup. No changes made."
        break
    fi

    # Find matching timezones
    mapfile -t matches < <(timedatectl list-timezones | grep -i "$search_term")

    if [ ${#matches[@]} -eq 0 ]; then
        echo "--- No matches found for '$search_term'. Please try again. ---"
        continue # Restart the loop to ask for a new search term
    fi

    echo "Matches found: ${#matches[@]}"
    echo "Please select the correct timezone or choose 'Search Again':"
    
    # Add 'Search Again' and 'Exit' to the menu options
    select opt in "${matches[@]}" "Search Again" "Exit Without Saving"; do
        case $opt in
            "Search Again")
                break # This breaks the 'select' menu but stays in the 'while' loop
                ;;
            "Exit Without Saving")
                echo "Exiting setup..."
                exit 0
                ;;
            *)
                if [ -n "$opt" ]; then
                    sudo timedatectl set-timezone "$opt"
                    echo "-----------------------------------------------"
                    echo "SUCCESS: Timezone set to $opt."
                    echo "The system time is now: $(date)"
                    echo "-----------------------------------------------"
                    exit 0 # Exit the entire script successfully
                else
                    echo "Invalid selection. Please pick a number from the list."
                fi
                ;;
        esac
    done
done