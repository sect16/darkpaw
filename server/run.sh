SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libatomic.so.1.2.0
cd $SCRIPT_DIR
python3 start.py
