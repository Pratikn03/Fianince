# ==============================================================================
# Vivado Synthesis & Implementation Script for AMIP FPGA Risk Pipeline
# Target Device: AMD Alveo U50 Data Center Accelerator (xcu50-fsvh2104-2-e)
# Clock Target: 400 MHz (Period: 2.500 ns)
# ==============================================================================

set TARGET_PART "xcu50-fsvh2104-2-e"
set TOP_MODULE "amip_fpga_pipeline"
set OUTPUT_DIR "./vivado_build"

file mkdir $OUTPUT_DIR

# 1. Read RTL Sources
read_verilog -sv ./agentic_guard/hardware/amip_fpga_pipeline.v

# 2. Define Timing Constraints
create_clock -period 2.500 -name clk [get_ports clk]
set_input_delay -clock clk 0.400 [all_inputs -no_clocks]
set_output_delay -clock clk 0.400 [all_outputs]

# 3. Out-of-Context Synthesis
synth_design -top $TOP_MODULE -part $TARGET_PART -mode out_of_context -flatten_hierarchy rebuilt

# 4. Implementation (Opt, Place, Route)
opt_design -directive Explore
place_design -directive Explore
phys_opt_design -directive AggressiveExplore
route_design -directive Explore

# 5. Generate Hardware Utilization & Timing Reports
report_utilization -file $OUTPUT_DIR/utilization_route.rpt -hierarchical
report_timing_summary -file $OUTPUT_DIR/timing_summary.rpt -max_paths 10
report_power -file $OUTPUT_DIR/power_analysis.rpt

puts "AMIP Synthesis and Implementation on AMD Alveo U50 completed successfully."
exit
