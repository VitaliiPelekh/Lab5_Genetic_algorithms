import matplotlib.pyplot as plt
import random
import json


class Schedule:
    def __init__(self, classes, teachers, subjects, rooms, days=5, lessons=5):
        self.classes = classes
        self.teachers = teachers
        self.subjects = subjects
        self.rooms = rooms
        self.days = days
        self.lessons = lessons
        self.schedule = self.initialize_schedule()

    def initialize_schedule(self):
        return [[[(random.choice(self.subjects), random.choice(self.teachers), random.choice(self.rooms))
                  for _ in range(self.lessons)] for _ in range(self.days)] for _ in range(self.classes)]


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, generations, elite_size):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.elite_size = elite_size
        self.fitness_over_time = []

    def initialize_population(self, base_schedule):
        return [Schedule(base_schedule.classes, base_schedule.teachers, base_schedule.subjects, base_schedule.rooms, base_schedule.days, base_schedule.lessons) for _ in range(self.population_size)]

    def fitness(self, schedule):
        score = 0
        for class_schedule in schedule.schedule:
            for day_schedule in class_schedule:
                teachers = [lesson[1] for lesson in day_schedule]
                subjects = [lesson[0] for lesson in day_schedule]
                rooms = [lesson[2] for lesson in day_schedule]

                # Check for the constraint of 'Physical Education', 'Choreography', 'Music' being in their respective rooms
                if 'Physical Education' in subjects and 'Gym' not in rooms:
                    score += 1
                if 'Choreography' in subjects and 'Dance Room' not in rooms:
                    score += 1
                if 'Music' in subjects and 'Music Room' not in rooms:
                    score += 1

                # Check for the constraint of 'Math', 'English', 'History', 'Geography' being in their respective rooms
                academic_subjects = ['Math', 'English', 'History', 'Geography']
                for subject in academic_subjects:
                    if subject in subjects and not any(
                            classroom in rooms for classroom in ['Classroom 1', 'Classroom 2', 'Classroom 3']):
                        score += 1

                # Check for the constraint of a teacher not teaching more than once a day
                if len(teachers) != len(set(teachers)):
                    score += 1

                # Check for the constraint of a subject not being taught more than once a day
                if len(subjects) != len(set(subjects)):
                    score += 1

                # Check for the constraint of a room not being used more than once a day
                if len(rooms) != len(set(rooms)):
                    score += 1

        # Check for the constraint of one teacher teaching at least half of the lessons for their class
        for class_schedule in schedule.schedule:
            all_teachers = [lesson[1] for day_schedule in class_schedule for lesson in day_schedule]
            most_common_teacher = max(set(all_teachers), key=all_teachers.count)
            if all_teachers.count(most_common_teacher) < len(all_teachers) // 2:
                score += 1

        return score

    def mutate(self, schedule):
        if random.random() < self.mutation_rate:
            day = random.randint(0, schedule.days - 1)
            lesson = random.randint(0, schedule.lessons - 1)
            class_ = random.randint(0, schedule.classes - 1)

            # Instead of selecting random subject, teacher, and room, we make sure to select valid ones
            subject = random.choice(schedule.subjects)
            if subject == 'Physical Education':
                room = 'Gym'
            elif subject == 'Choreography':
                room = 'Dance Room'
            elif subject == 'Music':
                room = 'Music Room'
            elif subject in ['Math', 'English', 'History', 'Geography']:
                room = random.choice(['Classroom 1', 'Classroom 2', 'Classroom 3'])
            else:
                room = random.choice(schedule.rooms)
            teacher = random.choice(schedule.teachers)
            schedule.schedule[class_][day][lesson] = (subject, teacher, room)
        return schedule

    def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            crossover_point = random.randint(0, parent1.classes - 1)
            child1 = parent1.schedule[:crossover_point] + parent2.schedule[crossover_point:]
            child2 = parent2.schedule[:crossover_point] + parent1.schedule[crossover_point:]
            parent1.schedule, parent2.schedule = child1, child2
        return parent1, parent2

    def post_process(self, schedule):
        for class_schedule in schedule.schedule:
            for day_schedule in class_schedule:
                subjects = [lesson[0] for lesson in day_schedule]
                rooms = [lesson[2] for lesson in day_schedule]

                for subject, room in zip(subjects, rooms):
                    if subject == 'Physical Education' and room != 'Gym':
                        room = 'Gym'
                    elif subject == 'Choreography' and room != 'Dance Room':
                        room = 'Dance Room'
                    elif subject == 'Music' and room != 'Music Room':
                        room = 'Music Room'
                    elif subject in ['Math', 'English', 'History', 'Geography'] and room not in ['Classroom 1', 'Classroom 2', 'Classroom 3']:
                        room = random.choice(['Classroom 1', 'Classroom 2', 'Classroom 3'])
        return schedule

    def optimize(self, schedule):
        population = sorted(self.initialize_population(schedule), key=self.fitness)
        for _ in range(self.generations):
            new_population = population[:self.elite_size]
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(population[:50], 2)
                child1, child2 = self.crossover(parent1, parent2)
                new_population += [self.post_process(self.mutate(child1)), self.post_process(self.mutate(child2))]
            population = sorted(new_population, key=self.fitness)
            self.fitness_over_time.append(self.fitness(population[0]))
        return population[0]

    def plot_fitness_over_time(self):
        plt.plot(self.fitness_over_time)
        plt.title('Fitness over time')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.show()


def pretty_print(schedule):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    classes = ['Class 1', 'Class 2', 'Class 3']

    for idx, class_schedule in enumerate(schedule):
        print(f'=== {classes[idx]} ===')
        for day_idx, day_schedule in enumerate(class_schedule):
            print(f'--- {days[day_idx]} ---')
            for period in day_schedule:
                print(f'  {period[0]} taught by {period[1]} in {period[2]}')
        print('\n')


def save_data(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file)


def load_data(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)


classes = 3
teachers = ['T1', 'T2', 'T3', 'T4']
subjects = ['Math', 'English', 'History', 'Geography', 'Physical Education', 'Choreography', 'Music']
rooms = ['Classroom 1', 'Classroom 2', 'Classroom 3', 'Gym', 'Dance Room', 'Music Room']
days = 5
lessons = 5

schedule = Schedule(classes, teachers, subjects, rooms, days, lessons)
ga = GeneticAlgorithm(100, 0.01, 0.7, 500, 20)
optimized_schedule = ga.optimize(schedule)
ga.plot_fitness_over_time()
pretty_print(optimized_schedule.schedule)

# Save data
data = {
    'classes': classes,
    'teachers': teachers,
    'subjects': subjects,
    'rooms': rooms,
    'days': days,
    'lessons': lessons
}
save_data(data, 'schedule_data.json')

# Load data
loaded_data = load_data('schedule_data.json')
classes = loaded_data['classes']
teachers = loaded_data['teachers']
subjects = loaded_data['subjects']
rooms = loaded_data['rooms']
days = loaded_data['days']
lessons = loaded_data['lessons']

# print(f"\n\nLoaded data: ")
# schedule = Schedule(classes, teachers, subjects, rooms, days, lessons)
# ga = GeneticAlgorithm(100, 0.01, 0.7, 500, 20)
# optimized_schedule = ga.optimize(schedule)
# pretty_print(optimized_schedule.schedule)
