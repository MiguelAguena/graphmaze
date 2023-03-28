LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;
USE ieee.math_real.ALL;

ENTITY clock_mul IS
    GENERIC (
        half_factor : NATURAL
    );
    PORT (
        clock : IN STD_LOGIC;
        mul_clock : OUT STD_LOGIC
    );
END ENTITY clock_mul;

ARCHITECTURE comportamental OF clock_mul IS
    SIGNAL clock_count : unsigned(NATURAL(ceil(log2(real(half_factor)))) - 1 DOWNTO 0);
    CONSTANT unit : unsigned(NATURAL(ceil(log2(real(half_factor)))) - 1 DOWNTO 0) := (0 => '1', others=> '0');
    SIGNAL s_mul_clock : STD_LOGIC := '0';
BEGIN
    PROCESS (clock)
    BEGIN
        IF (clock'event AND clock = '1') THEN
            clock_count <= clock_count + unit;
            IF clock_count = 0 THEN
                s_mul_clock <= NOT s_mul_clock;
            END IF;
        END IF;
    END PROCESS;
    mul_clock <= s_mul_clock;
END ARCHITECTURE comportamental;