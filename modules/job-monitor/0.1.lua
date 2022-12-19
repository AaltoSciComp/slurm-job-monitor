-- -*- lua -*-

whatis([[Name : job-monitor]])
whatis([[Version : 0.1]])
help([[This tool uses telegraf to monitor CPU and GPU usage during Slurm jobs' runtime.]])

--if not isloaded("telegraf/1.23.0") then
--load("telegraf/1.23.0")
--end
--

local fn = myFileName()
local full = myModuleFullName()
local loc = fn:find(full,1,true)-2
local mdir = fn:sub(1,loc)
local root = mdir .. "/../"

prepend_path("PATH", root .. "bin")
setenv("JOB_MONITOR_CONFIG_DIR", root .. "etc")
setenv("JOB_MONITOR_GATHER_INTERVAL", "10s")
setenv("JOB_MONITOR_FLUSH_INTERVAL", "120s")
setenv("JOB_MONITOR_AVERAGE_INTERVAL", "60s")
