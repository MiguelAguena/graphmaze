@REM @echo off
@REM ghdl -a *.vhd --ieee=synopsys
@REM ghdl -a cordic_tb.vhd
@REM ghdl -e cordic_tb
@REM ghdl -r cordic_tb

ghdl -a graphmaze.vhd
ghdl -a vhdl/hadamard/flux_multiplier_tb.vhd
ghdl -e flux_multiplier_tb
ghdl -r flux_multiplier_tb --wave=ondas.ghw
del *.cf