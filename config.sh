# Define custom utilities
# Test for OSX with [ -n "$IS_OSX" ]

function pre_build {
    # Any stuff that you need to do before you start building the wheels
    # Runs in the root directory of this repository.
    :
}

function run_tests {
    # check we have the expected version and architecture for Python
    python -c "import sys; print(sys.version)"
    python -c "import struct; print(struct.calcsize('P') * 8)"
    # run the test suite
    pytest -v ../tests
}
