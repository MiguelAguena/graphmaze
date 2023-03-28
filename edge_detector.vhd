--------------------------------------------------------------------------
-- Arquivo   : edge_detector.vhd
-- Projeto   : Experiencia 04 - Desenvolvimento de Projeto de
--                              Circuitos Digitais com FPGA
--------------------------------------------------------------------------
-- Descricao : detector de borda
--             gera um pulso na saida de 1 periodo de clock
--             a partir da detecao da borda de subida sa entrada
--
--             sinal de reset ativo em alto
--
--             > adaptado a partir de codigo VHDL disponivel em
--               https://surf-vhdl.com/how-to-design-a-good-edge-detector/
--------------------------------------------------------------------------
-- Revisoes  :
--     Data        Versao  Autor             Descricao
--     29/01/2020  1.0     Edson Midorikawa  criacao
--     27/01/2021  1.1     Edson Midorikawa  revisao
--     29/01/2023  1.2     Edson Midorikawa  revisao
--------------------------------------------------------------------------

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;

ENTITY edge_detector IS
    PORT (
        clock : IN STD_LOGIC;
        reset : IN STD_LOGIC;
        sinal : IN STD_LOGIC;
        pulso : OUT STD_LOGIC
    );
END ENTITY edge_detector;

ARCHITECTURE rtl OF edge_detector IS

    SIGNAL reg0, reg1 : STD_LOGIC := '0';

BEGIN

    detector : PROCESS (clock, reset)
    BEGIN
        IF (reset = '1') THEN
            reg0 <= '0';
            reg1 <= '0';
        ELSIF (rising_edge(clock)) THEN
            reg0 <= sinal;
            reg1 <= reg0;
        END IF;
    END PROCESS;

    pulso <= NOT reg1 AND reg0;

END ARCHITECTURE rtl;