#!/bin/bash -x
# npx prettier --write --svelte-sort-order scripts-markup-styles ./src/**/*.svelte

export NODE_OPTIONS="--max_old_space_size=4096"
export NODE_ENV=production

# SPACE=$(git branch --show-current)
SPACE=$1

if [ -z "$SPACE" ]; then  
	echo "Space parameter is missing"; 
	exit
fi

if [ ! -f "./src/space_config/${SPACE}.js" ]; then
	echo "${SPACE}.js does not exist."
	exit
fi

unlink src/space_config/index.js
cd src/space_config
ln -s ${SPACE}.js index.js
cd ../..

time npm run build
rsync -av -q --delete dist/ "../run/public/${SPACE}"
