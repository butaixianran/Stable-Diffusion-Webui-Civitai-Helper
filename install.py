import launch

if not launch.is_installed("pysocks"):
    launch.run_pip("install pysocks", "pysocks")
