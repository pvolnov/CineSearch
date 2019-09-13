export SERVER='VDS1'
# dos2unix start.sh
cmd() { python3 telsent.py; }
echo "Start script"

until cmd; do
    if [ $? -eq 0 ]; then
        exit 0
    else
        echo "Restarting"
    fi
    # potentially, other code follows...
done

