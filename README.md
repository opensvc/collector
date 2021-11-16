Opensvc collector
=================

https://github.com/opensvc/collector

This package provides the code to run Opensvc Collector

https://collector.opensvc.com


githook pre-commit
==================

This githook ensure fresh static files are served when new release is done.
static files are served from this location based on git HEAD ref

## .git/hooks/pre-commit

	cat > .git/hooks/pre-commit <<-EOF
	CID="\$(git show HEAD | head -n 1 | awk '{print \$NF}')"
	echo "code_rev=\"\$CID\"" > $PWD/init/models/version.py
	git add init/models/version.py
	EOF
	chmod +x .git/hooks/pre-commit
