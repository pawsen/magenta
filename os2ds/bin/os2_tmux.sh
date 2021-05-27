#!/usr/bin/env bash

set -eEu -o pipefail
# set -x

OS2DS_PATH="$HOME/git/os2datascanner"
OS2DS_ENGINE_USER_CONFIG_PATH=$OS2DS_PATH/dev-environment/engine/dev-settings.toml
OS2DS_ADMIN_USER_CONFIG_PATH=$OS2DS_PATH/dev-environment/admin/dev-settings.toml
OS2DS_REPORT_USER_CONFIG_PATH=$OS2DS_PATH/dev-environment/report/dev-settings.toml

ENGINE_FLAGS="--debug --log debug"

ENGINE_MODULES=('explorer' 'processor' 'matcher' 'tagger' 'exporter')
DJANGO_MODULES=('report' 'admin')

#######################################
# Check if variable is in array
# Arguments:
#   description, variable, array
# Returns
#   0 if var is in the array, exit 1 if not
# Example
#   is_in_array "engine" "matcher"  ("matcher" "tagger" "exporter")
########################################
is_in_array() {
    local desc="$1"
    local var="$2"
    shift 2 # Removes $1 & $2 from the parameter list
    local arr="$@"
    if [[ ! " ${arr[@]} " =~ " ${var} " ]]; then
        echo "${desc}: ${var} not in list: '${arr}'"
        exit 1
    fi
}


########################################
# Trap any error code and display on which line the error occurred
# Nb. Use `set -eE` and not only `set -e` to ensure errors in functions are also
# trap'ed.
########################################
print_error() {
    read line file <<<$(caller)
    echo "An error occurred in line $line of file $file:" >&2
    sed "${line}q;d" "$file" >&2
}
trap print_error ERR


print_usage() {
  # https://stackoverflow.com/a/3588939
  printf "Usage: %s [-e val] [-d val] [-w]\n" ${0##*/}
  echo "Run engine modules admin/report pipeline_collector in tmux"
  echo "-e engine module. One '-e' for each module in '${ENGINE_MODULES[@]} worker'"
  echo "-w. worker module"
  echo "-d django pipeline_collector. One of '${DJANGO_MODULES[@]}'"
  echo \
  "Running without any arguments will start all the engine modules and none django"
}


declare -a engine=() django=()
while getopts "he:d:w" opt; do
    case ${opt} in
        h) print_usage && exit 0 ;;
        e)
            is_in_array "ENGINE" "$OPTARG" "${ENGINE_MODULES[@]} worker"
            engine+=("$OPTARG")
            ;;
        ea)
            echo "here"
            ;;
        d)
            is_in_array "DJANGO" "$OPTARG" "${DJANGO_MODULES[@]}"
            django+=("$OPTARG")
            ;;
        w)
            engine+=("worker")
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            print_usage
            exit 1
            ;;
    esac
done
shift $((OPTIND -1))

# test if length of array is non-zero
if ! (( ${#engine[@]} )); then
    engine=(${ENGINE_MODULES[@]})
fi
echo "starting engine modules: ${engine[@]}"

if (( ${#django[@]} )); then
    echo "Starting Django (${django[@]})_pipeline_collector"
else
    echo "Not starting Django modules"
fi

# start server to avoid error when calling `tmux list session`
tmux start-server
SESSION="os2ds"
# grep exit with 1 if there's no match. With set -e, this makes the script exit.
# || (else) returns true (0) if the exit code($?) of grep `is 1.
# https://unix.stackexchange.com/a/427598
SESSIONEXISTS=$(tmux list-sessions | grep $SESSION  || [[ $? == 1 ]])
# Only create tmux session if it doesn't already exist
if [ "$SESSIONEXISTS" = "" ]
then
    # create new detached session
    tmux new-session -d -s $SESSION -c "$OS2DS_PATH"
    #tmux rename-window -t $SESSION "$module"
    # index is given as: -t {session_name}:{window_index}.{pane_index}.
    for module in "${engine[@]}"; do
        tmux new-window -t $SESSION: -c $OS2DS_PATH -n "$module"
        tmux send-keys -t "$module" "OS2DS_ENGINE_USER_CONFIG_PATH=$OS2DS_ENGINE_USER_CONFIG_PATH python -m os2datascanner.engine2.pipeline.run_stage $module $ENGINE_FLAGS" C-m
    done

    for module in "${django[@]}"; do
        #capitalize module
        mod_cap=$(tr '/a-z/' '/A-Z/' <<< $module)
        tmux new-window -t $SESSION: -c $OS2DS_PATH -n "$module"
        tmux send-keys -t "$module" "OS2DS_${mod_cap}_USER_CONFIG_PATH=dev-environment/${module}/dev-settings.toml DJANGO_SETTINGS_MODULE=os2datascanner.projects.${module}.settings python -m os2datascanner.projects.${module}.manage pipeline_collector" C-m
    done

    # kill the first window
    tmux kill-window -t $SESSION:1
    echo "tmux started. Attach with 'tmux attach-session -t ${SESSION}:'"
else
    echo "tmux not started. Session ${SESSION} already running"
    echo "use 'tmux kill-session' to kill it"
fi


# Attach Session. with :, attach to last created/active window
#tmux attach-session -t $SESSION:
