@echo off
rem This command turns off the echoing of commands to the console.

echo "Starting entrypoint script..."

rem Get the first command-line argument.
rem In a batch script, %1 is the first argument, %2 is the second, and so on.
rem %~1 removes any surrounding quotes from the argument.

if "%~1" == "" (
    echo "Usage: %0 {python}"
    echo "Usage: {help | test}"
    exit /b 1
)

if "%~1" == "help" (
    echo "This is an automated test script for unit tests."
    echo "Usage: {python} {help | test}"
    echo "Example: python test"
    exit /b 0
)

if "%~1" == "test" (
    echo "Running unit tests..."
    OpenCtrlEnv\Scripts\activate
    python -m controls.test
    echo "Unit tests completed."
    exit /b 0
)

rem If the argument doesn't match any of the above, print an error.
echo "Invalid argument: %~1"
echo "Usage: {python} {help | test}"
exit /b 1
