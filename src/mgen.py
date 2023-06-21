
from algorithms.genetic import generate_genome, Genome, selection_pair, single_point_crossover, mutation
import os
import json
from pathlib import Path
from typing import List, Dict
from midiutil import MIDIFile
from pyo import *

songs_path = os.path.join(Path(__file__).parent, "static")


BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F",
        "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian",
          "lydian", "mixolydian", "majorBlues", "minorBlues"]


def int_from_bits(bits: List[int]) -> int:

    return int(sum([bit*pow(2, index) for index, bit in enumerate(bits)]))


def genome_to_melody(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int) -> Dict[str, list]:
    notes = [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE]
             for i in range(num_bars * num_notes)]

    note_length = 4 / float(num_notes)

    scl = EventScale(root=key, scale=scale, first=root)

    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    for note in notes:
        integer = int_from_bits(note)

        if not pauses:
            integer = int(integer % pow(2, BITS_PER_NOTE - 1))

        if integer >= pow(2, BITS_PER_NOTE - 1):
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]

    steps = []
    for step in range(num_steps):
        steps.append([scl[(note+step*2) % len(scl)]
                     for note in melody["notes"]])

    melody["notes"] = steps
    return melody


def genome_to_events(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int, bpm: int) -> [Events]:
    melody = genome_to_melody(
        genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            attack=0.001,
            decay=0.05,
            sustain=0.5,
            release=0.005,
            bpm=bpm
        ) for step in melody["notes"]
    ]


def metronome(bpm: int):
    met = Metro(time=1 / (bpm / 60.0)).play()
    t = CosTable([(0, 0), (50, 1), (200, .3), (500, 0)])
    amp = TrigEnv(met, table=t, dur=.25, mul=1)
    freq = Iter(met, choice=[660, 440, 440, 440])
    return Sine(freq=freq, mul=amp).mix(2).out()


def save_genome_to_midi(filename: str, genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                        pauses: bool, key: str, scale: str, root: int, bpm: int):
    melody = genome_to_melody(
        genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track = 0
    channel = 0

    time = 0.0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i],
                           time, melody["beat"][i], vel)

        time += melody["beat"][i]

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)


def generate(rating_list, num_mutations, mutation_probability, global_pop, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm):
    population = global_pop
    random.shuffle(population)
    population_fitness = []
    for index, genome in enumerate(population):
        population_fitness.append((genome, rating_list[index]))

    sorted_population_fitness = sorted(
        population_fitness, key=lambda e: e[1], reverse=True)

    population = [e[0] for e in sorted_population_fitness]

    next_generation = population[0:2]

    for j in range(int(len(population) / 2) - 1):

        def fitness_lookup(genome):
            for e in population_fitness:
                if e[0] == genome:
                    return e[1]
            return 0

        parents = selection_pair(population, fitness_lookup)
        offspring_a, offspring_b = single_point_crossover(
            parents[0], parents[1])
        offspring_a = mutation(
            offspring_a, num=num_mutations, probability=mutation_probability)
        offspring_b = mutation(
            offspring_b, num=num_mutations, probability=mutation_probability)
        next_generation += [offspring_a, offspring_b]
        save_to_genome(population, num_bars, num_notes,
                       num_steps, pauses, key, scale, root, bpm)
        return next_generation


def save_to_genome(population, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm):
    for i, genome in enumerate(population):
        save_genome_to_midi(os.path.join(
            songs_path, f"{i}.mid"), genome, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)


def main(num_bars: int, num_notes: int, num_steps: int, pauses: bool, key: str, scale: str, root: int,
         population_size: int, num_mutations: int, mutation_probability: float, bpm: int):

    population = [generate_genome(num_bars * num_notes * BITS_PER_NOTE)
                  for _ in range(population_size)]

    save_to_genome(population, num_bars, num_notes,
                   num_steps, pauses, key, scale, root, bpm)

    return population


if __name__ == '__main__':
    main()
