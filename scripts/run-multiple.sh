ID_LIST=(87 89)
for i in "${ID_LIST[@]}"
do
	cd $(find ~/miniguc/runs/0$i*/ | head -n 1)
	time mpirun -np 4 ./wrf.exe
done

cd ~/miniguc/scripts
