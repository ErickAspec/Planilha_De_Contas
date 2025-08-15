import time

# Função para digitar letra por letra
def type_text(text, delay=0.07):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

# Trecho da música aumentado
lyrics = [
    "I wanna da—, I wanna dance in the lights",
    "I wanna ro—, I wanna rock yo' body",
    "I wanna go, I wanna go for a ride",
    "Hop in the music and rock yo' body right",
    "Feel the rhythm, let it take control",
    "Move your body, let the music roll",
    "Tonight's the night, we're gonna lose our mind"
]

# Execução
for line in lyrics:
    type_text(line)
    time.sleep(0.7)  # pequena pausa entre as linhas
