#!/usr/bin/bash

combination_folder_path="$1"
benchmarks="BT LU SP EP MG CG"

cd $combination_folder_path
for bench in $benchmarks; do
	if [ -d $bench ]; then
		bench_lower=$(echo "$bench" | tr '[:upper:]' '[:lower:]')
		make veryclean
		make $bench CLASS=C
		rm -f bin/$bench_lower.C.x
		rm -f common/wtime_sgi64.c
	fi
done


#combination_folder_path="$1"
#bencmark_name=AU
#bencmark_name_lower=$(echo "$bencmark_name" | tr '[:upper:]' '[:lower:]')
#cd $combination_folder_path
#make veryclean
#make $bencmark_name CLASS=C
#rm -f bin/$bencmark_name_lower.C.x
#rm -f common/wtime_sgi64.cft
