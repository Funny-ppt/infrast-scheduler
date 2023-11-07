branch_name=$1

cd ../InfrastSim
git checkout $branch_name
git branch --set-upstream-to=origin/$branch_name $branch_name
git pull
dotnet publish -r linux-x64 InfrastSimExports
cd ../infrast-scheduler
cp /home/funny_ppt/src/InfrastSim/InfrastSimExports/bin/Release/net8.0/linux-x64/publish/InfrastSimExports.so ./lib/InfrastSim.so