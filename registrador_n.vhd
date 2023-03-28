LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY registrador_n IS
    GENERIC (
        N : INTEGER := 8;
        reset_value : NATURAL
    );
    PORT (
        clock : IN STD_LOGIC;
        reset : IN STD_LOGIC;
        load : IN STD_LOGIC;
        D : IN STD_LOGIC_VECTOR (N - 1 DOWNTO 0);
        Q : OUT STD_LOGIC_VECTOR (N - 1 DOWNTO 0)
    );
END ENTITY registrador_n;

ARCHITECTURE comportamental OF registrador_n IS
    SIGNAL IQ : STD_LOGIC_VECTOR(N - 1 DOWNTO 0) := STD_LOGIC_VECTOR(to_unsigned(reset_value, n));
BEGIN

    PROCESS (clock)
    BEGIN
        IF (rising_edge(clock)) THEN
            IF (reset = '1') THEN
                IQ <= STD_LOGIC_VECTOR(to_unsigned(reset_value, n));
            ELSIF (load = '1') THEN
                IQ <= D;
            ELSE
                IQ <= IQ;
            END IF;
        END IF;
    END PROCESS;
    Q <= IQ;

END ARCHITECTURE comportamental;