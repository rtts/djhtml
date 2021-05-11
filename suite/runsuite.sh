#!/bin/bash

function convert {
	OUT=$(mktemp)
	cp $TESTCASE/input.html $OUT
	djhtml $OUT
	cat $OUT
	rm $OUT
}

CASES=0
FAILURES=0
for TESTCASE in */; do
	echo -n "Evaluating ${TESTCASE}...   "
	CASES=$((CASES+1))
	if cmp <(convert "${TESTCASE}input.html") "${TESTCASE}expected.html"; then
		echo "OK"
	else
		FAILURES=$((FAILURES+1))
		echo "NO"
		diff <(convert "${TESTCASE}input.html") "${TESTCASE}expected.html"
	fi
done

if [ "${FAILURES}" == 0 ]; then
	echo "All ${CASES} cases passed."
else
	echo "Number of failures: ${FAILURES} out of ${CASES}"
	exit 1
fi
