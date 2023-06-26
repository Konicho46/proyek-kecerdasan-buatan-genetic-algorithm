import random
from operator import attrgetter
#Evolution
def blend_colors(color1, color2, ratio=0.5):
    blended_color = (
        int(color1[0] * ratio + color2[0] * (1 - ratio)),
        int(color1[1] * ratio + color2[1] * (1 - ratio)),
        int(color1[2] * ratio + color2[2] * (1 - ratio))
    )
    return blended_color

def bound_value(v, min_v, max_v):
    return min(max(min_v, v), max_v)

# Fungsi yang menghasilkan keturunan yang baru
def recombinate(pairs, gene_props, mutation_probability=0.1, effect=0.5):
    offspring = []
    for p1, p2 in pairs:
        children_genes = {}
        for gen in p1.genes.keys():
            values = [p1.genes[gen], p2.genes[gen]]
            if gen == "colors":
                children_genes[gen] = blend_colors(min(values), max(values))
            else:
                children_genes[gen] = random.uniform(min(values), max(values))
                if random.random() < mutation_probability:
                    min_v = gene_props[gen]['min']
                    max_v = gene_props[gen]['max']
                    v = children_genes[gen]
                    rv = random.choice([-1, 1]) * random.uniform(0, effect * (max_v - min_v))
                    new_v = bound_value(v + rv, min_v, max_v)
                    children_genes[gen] = new_v
        offspring.append(children_genes)
    return offspring

# Fungsi ini juga digunakan untuk memilih pasangan individu untuk perkawinan, namun menggunakan metode turnamen.
# Individu dipilih secara acak dan dibandingkan berdasarkan fitness mereka.
def mating_pool_tournament(population, num_of_pairs=10, evaluator=attrgetter('fitness')):
    pool = []
    while len(pool) < num_of_pairs:
        # Generate a pair for mating
        # misal ada 6 invader terus evaluator e dari fitness e sendiri-sendiri
        # dimasukan kedalam turnamen
        p1 = tournament(population, evaluator)
        # Masuk turnamen namun p1 dikeluarin dari populasi
        p2 = tournament(population - {p1}, evaluator)
        # Jika turnamen p1 dan p2 sudah selesai melakukan turnamen, maka diappend masuk kedalam array pool
        pool.append((p1, p2))
    return pool

# Fungsi ini mengimplementasikan metode turnamen untuk memilih individu dari populasi.
# Beberapa individu dipilih secara acak dari populasi dan dibandingkan berdasarkan fitness mereka.
# Individu dengan fitness tertinggi dipilih sebagai hasil turnamen.
def tournament(population, evaluator, k=2):
    # sample adalah populasi
    # Jika populasi lebih dari k = maka sample ngampil 2 populasi random
    # Jika banyaknya populasi leibh kecil dari k maka populasi tersebut masuk kedalam sample
    sample = population if len(population) < k else random.sample(population, k)
    return max(sample, key=evaluator)