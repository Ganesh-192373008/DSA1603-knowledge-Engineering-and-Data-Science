# Q4: University course-advising ontology with owlready2 + HermiT reasoner
from owlready2 import *

onto = get_ontology("http://example.org/advising.owl")

with onto:
    # ---------- 1. Class hierarchy ----------
    class Course(Thing): pass
    class CoreCourse(Course): pass
    class ElectiveCourse(Course): pass
    class Topic(Thing): pass
    class DatabaseTopic(Topic): pass
    class ProgrammingTopic(Topic): pass
    class MathTopic(Topic): pass
    class Student(Thing): pass

    # ---------- 2. Object properties ----------
    class hasCompleted(ObjectProperty):         domain = [Student];        range = [Course]
    class requiresPrerequisite(ObjectProperty): domain = [ElectiveCourse]; range = [Course]
    class coversTopic(ObjectProperty):          domain = [Course];         range = [Topic]
    class isSynonymOf(ObjectProperty, SymmetricProperty, TransitiveProperty):
        domain = [Topic]; range = [Topic]
    class hasLearned(ObjectProperty):           domain = [Student];        range = [Topic]

    # inference rules expressed as OWL property chains
    hasLearned.property_chain.append(PropertyChain([hasCompleted, coversTopic]))  # completed course -> learned its topics
    hasLearned.property_chain.append(PropertyChain([hasLearned, isSynonymOf]))    # learned a topic -> learned its synonyms

    # ---------- 3. Individuals: topics (is-a their topic class) and synonyms ----------
    dbms      = DatabaseTopic("DBMS")
    db_sys    = DatabaseTopic("DatabaseSystems")
    sql       = DatabaseTopic("SQL")                  # SQL is-a DatabaseTopic
    python_t  = ProgrammingTopic("Python")
    prog      = ProgrammingTopic("ProgrammingBasics")
    stats     = MathTopic("Statistics")
    dbms.isSynonymOf  = [db_sys]                      # "DBMS" == "Database Systems"
    python_t.isSynonymOf = [prog]                     # "Python" == "Programming Basics"

    # ---------- courses ----------
    cs101 = CoreCourse("CS101_Programming");     cs101.coversTopic = [prog]
    cs102 = CoreCourse("CS102_DatabaseSystems"); cs102.coversTopic = [db_sys, sql]
    cs103 = CoreCourse("CS103_Statistics");      cs103.coversTopic = [stats]
    cs104 = CoreCourse("CS104_DBMS");            cs104.coversTopic = [dbms]
    e301 = ElectiveCourse("E301_AdvancedSQL");    e301.requiresPrerequisite = [cs102]
    e302 = ElectiveCourse("E302_MachineLearning");e302.requiresPrerequisite = [cs101, cs103]
    e303 = ElectiveCourse("E303_DataMining");     e303.requiresPrerequisite = [cs104, cs103]

    # ---------- students and the courses they completed ----------
    asha   = Student("Asha");   asha.hasCompleted   = [cs101, cs102, cs103]
    ravi   = Student("Ravi");   ravi.hasCompleted   = [cs104, cs103]
    meena  = Student("Meena");  meena.hasCompleted  = [cs101]
    karthik= Student("Karthik");karthik.hasCompleted= [cs101, cs103]

    # ---------- defined (equivalent) classes: eligibility for each elective ----------
    class EligibleForAdvancedSQL(Student):
        equivalent_to = [Student & hasLearned.value(dbms) & hasLearned.value(sql)]
    class EligibleForMachineLearning(Student):
        equivalent_to = [Student & hasLearned.value(python_t) & hasLearned.value(stats)]
    class EligibleForDataMining(Student):
        equivalent_to = [Student & hasLearned.value(dbms) & hasLearned.value(stats)]

print("Class hierarchy")
for c in [Course, CoreCourse, ElectiveCourse, Topic, DatabaseTopic, ProgrammingTopic, MathTopic, Student]:
    print(f"  {c.name:<17} subclass-of {c.is_a[0].name}")
print("Object properties:", [p.name for p in [hasCompleted, requiresPrerequisite, coversTopic, isSynonymOf, hasLearned]])
print("Synonyms: DBMS == DatabaseSystems ; Python == ProgrammingBasics")
print("Prerequisites declared:")
for e in [e301, e302, e303]:
    print(f"  {e.name:<20} requires {sorted(p.name for p in e.requiresPrerequisite)}")

# ---------- 4. Run the reasoner ----------
sync_reasoner_hermit(infer_property_values=True)      # needs Java; use sync_reasoner_pellet() for Pellet

print("\nTopics learned by each student (after reasoning, synonyms included)")
for s in [asha, ravi, meena, karthik]:
    print(f"  {s.name:<8}: {sorted(t.name for t in s.hasLearned)}")

print("\nInferred eligibility for electives")
checks = [("AdvancedSQL", EligibleForAdvancedSQL), ("MachineLearning", EligibleForMachineLearning),
          ("DataMining", EligibleForDataMining)]
for s in [asha, ravi, meena, karthik]:
    ok = [name for name, cls in checks if isinstance(s, cls)]
    print(f"  {s.name:<8}-> {', '.join(ok) if ok else 'none'}")
