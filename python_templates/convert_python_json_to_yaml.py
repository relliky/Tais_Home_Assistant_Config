import yaml
import json


python_dict = {'tool': 'xcelium', 'log': 'sim.log', 'sv_seed': '-486469063', 'build_dir': '/user/vich.tmp5/Projects/catapult_ppa/catapult-ino/sim/build_ttf_xc_RT_SHOWCASE_23_03_20_15_09', 'run_dir': '/user/vich.tmp5/Projects/catapult_ppa/catapult-ino/sim/regression_ttf_xc_RT_SHOWCASE_23_03_20_15_09/c11_top_sting_test_csrs/user/hpmcounterxh/hpmcounterxh_rd_only_0107_-486469063.816557111', 'test_name': 'c11_top_sting_test', 'coverage': False, 'no_upload': False, 'debug': False, 'gui': False, 'verdi': False, 'wave': None, 'input_tcl': None, 'clean': False, 'archive': False, 'overwrite': False, 'waiver': None, 'csim': True, 'sv_lib': ['$PROJECT_ROOT/riscv-model-cpu/build_svdpi/toplevel/dpimodel/libcatapult-dpi.so', '$PROJECT_ROOT/verif/ttf/csim_wrapper/csim_shim.so'], 'timeout': None, 'uvm_maxerror': 2, 'ticket': None, 'uvm_verbosity': 'UVM_LOW', 'xprop': False, 'xrun_xlog': False, 'maxerror': '2', 'sting_outputs_only': False, 'RUN_ARGS': ['+UVM_TESTNAME=c11_top_sting_test', '+AVS_TESTNAME=csrs/user/hpmcounterxh/hpmcounterxh_rd_only', '+AVS_STING', '+AVS_OPT=--seed=816557111', '+AVS_RUN', '+S_TCM_BACKDOOR', '+INIT_TCM'], 'BUILD_ARGS': ['-top', 'tb_top', '+define+TTF_ENABLE+BIU_CHECKER_ENABLE', '-access', '+rw'], 'build_model': True, 'compile_switches': None, 'config': 'RT_SHOWCASE', 'cwd': '$PROJECT_ROOT/sim', 'filelist': 'filelist.f', 'no_config': False, 'no_xmfile_msgcntl': True, 'power_intent': None, 'skip_svdpi': False, 'tech_build': False, 'x_behaviour': 'realistic'}

with open('python_database.yaml', 'w') as yaml_file:
    yaml.dump(python_dict, yaml_file, indent=2)

