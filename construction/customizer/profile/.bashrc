# pretty colors!
reset=$(tput sgr0)
bold=$(tput bold)
green=$(tput setaf 2)
magenta=$(tput setaf 5)
cyan=$(tput setaf 6)
white=$(tput setaf 7)

# git prompt and completion
source ~/config/git/git-prompt.sh
source ~/config/git/git-completion.bash

export GIT_PS1_SHOWDIRTYSTATE=1
export GIT_PS1_SHOWCOLORHINTS=1
export GIT_PS1_SHOWUNTRACKEDFILES=1

# command prompt
PROMPT_COMMAND='__git_ps1 "\[$reset\]\[$green\]\\u\[$bold\]@\[$reset\]\[$green\]$CONTAINER_NAME\[$reset\]\[$white\] \\w\[$reset\]" "\[$reset\] \[$green\]\\$ \[$reset\]"'

# git aliases
alias gst='git status -s'
alias gdiff='git d'
alias gdm='gdiff master --'

# rachel grep
function rgrep { grep -rni --exclude-dir '.ipynb_checkpoints' --exclude-dir '__pycache__' "$1" . --color=auto; }

# unlimited history. an elephant never forgets.
HISTSIZE=-1
HISTFILESIZE=-1