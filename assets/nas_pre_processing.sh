combination_folder_path="$1"
bencmark_name=AU
bencmark_name_lower=$(echo "$bencmark_name" | tr '[:upper:]' '[:lower:]')
cd $combination_folder_path
make veryclean
make $bencmark_name CLASS=C
rm bin/$bencmark_name_lower.C.x
rm common/wtime_sgi64.cft
