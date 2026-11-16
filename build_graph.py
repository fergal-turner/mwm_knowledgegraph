#!/usr/bin/env python3
"""Build a source-traceable graph from the supplied menu workbook."""

import argparse
import csv
import difflib
import hashlib
import re
import unicodedata
from collections import Counter, defaultdict, deque
from pathlib import Path

import openpyxl


# Curated from the menu's definitions, not an automatic causal inference.
# Rows: menu row | level | component activities | intermediate results |
# child outcomes | indicator targets. Indicator target syntax: q/l for
# quantity/quality of the menu item, r:<result>, o:<outcome>.
ROWS = """
5|system|Pay teachers in full and on time;Harmonise teacher pay scales|fair_teacher_compensation||q;q;l
6|system|Recognise displaced teachers' qualifications;Grant displaced teachers the right to work|teacher_professional_recognition||q;q
7|system|Provide sustained certified in-service training|teacher_professional_recognition||q;q
8|system|Define teacher promotion pathways;Offer teacher scholarships and advancement|teacher_career_progression||l;q
9|school_community|Establish predictable daily school routines||wellbeing|l;o:wellbeing
10|school_community|Provide cash for schooling-related costs;Monitor pupil attendance||access|o:access;o:access;o:access
11|system|Include displacement status in education data;Coordinate policy for displaced learners|displaced_learner_inclusion||l;l
12|class|Integrate guided play into curriculum;Train teachers in playful instruction|student_engagement;teaching_practice||l
13|school_community|Provide guided play and games in child-friendly spaces;Train community play facilitators||wellbeing|q;o:wellbeing
14|school_community|Deliver movement and cooperative games;Deliver songs and breathing activities||wellbeing|q;o:wellbeing
15|school_community|Install water points and treatment;Construct and maintain private latrines||wellbeing|q;q;o:access
16|school_community|Provide soap and handwashing facilities;Deliver hygiene education and behaviour-change activities||wellbeing|o:wellbeing;q;o:access
17|school_community|Provide private gender-segregated toilets and washing facilities|| |l;o:access;q
19|school_community|Screen children and route by assessed need;Provide support at different intensities|service_access||q;l;q;l
20|system|Provide layered family, community and specialised support;Screen children and refer to appropriate care|service_access||q;l;l;q
21|class|Train teachers in positive discipline and self-regulation|| |q;o:wellbeing
22|class|Teach children to recognise unsafe situations and report violence||wellbeing|q;o:wellbeing;o:wellbeing
23|school_community|Create safe violence reporting routes;Refer reported cases to protection, health or welfare services|service_access||l;q;q
24|school_community|Develop whole-school violence prevention plans;Revise school rules and practices with the school community||wellbeing|l;q;q;o:wellbeing
25|school_community|Define and distribute teacher codes of conduct;Enforce accountability for prohibited behaviour|school_accountability||l;q;q
26|school_community|Deliver condensed primary curriculum for over-age learners||access|o:access;q
27|school_community|Run non-formal community learning centres||access;learning|o:access;o:learning
28|school_community|Build awareness of students' identities;Co-create inclusive learning spaces with students|||q;r:belonging
29|class|Teach peace and perspective-taking;Bring learners from different groups together|intergroup_relations|wellbeing|q;r:intergroup_relations;o:wellbeing
30|class|Co-design digital learning content with displaced communities;Localise digital content to learners' language and curriculum|contextualised_content||q;l
31|class|Provide adaptive self-paced learning exercises;Give learners immediate feedback and rewards||learning|q;q;o:learning
32|class|Provide portable devices and offline learning content||access|q;q;o:access
33|class|Broadcast lessons through radio and interactive audio||access|q;o:access
34|class|Train teachers in disability awareness and inclusive pedagogy|teacher_inclusion_capacity||q;r:teacher_inclusion_capacity
35|class|Provide targeted literacy and numeracy instruction;Provide assistive devices and rehabilitation||learning|o:learning;q
36|school_community|Provide disability-specific learner support;Include learners with disabilities in mainstream activities|inclusion||l
37|system|Implement inclusive education policy;Make school buildings and materials accessible;Adopt school-wide anti-bullying policies|inclusion||q;q;r:inclusion
38|class|Provide teacher SEL and stress-management programmes|teacher_wellbeing||q;r:teacher_wellbeing
39|school_community|Schedule teacher collaboration time;Include teachers in school decision-making|supportive_leadership||q;r:supportive_leadership;l
40|school_community|Manage teacher workload and class size|teacher_wellbeing||q;q;q
41|system|Register and track displaced learners' enrolment and needs|displaced_learner_inclusion||q;q
42|system|Disaggregate education results by displacement status;Monitor differences between displaced and host learners|equity_monitoring||l;r:equity_monitoring
43|class|Teach in learners' home language||learning;wellbeing|q;q
44|class|Provide targeted host-language instruction||learning|q;o:learning
45|class|Deliver bilingual accelerated or remedial curriculum||learning|l;o:learning
46|school_community|Deliver painting and drawing with trained art therapists||wellbeing|q;o:wellbeing
47|school_community|Deliver theatre with trained drama therapists||wellbeing|q;o:wellbeing
48|school_community|Use instruments for non-verbal expression with music therapists||wellbeing|q;o:wellbeing
49|school_community|Create trauma narratives through writing;Use storytelling and drawing to explore identity||wellbeing|q;o:wellbeing
50|school_community|Provide centre-based early stimulation and preschool learning|school_readiness|learning|q;o:learning
51|school_community|Provide early childhood programmes for refugee language acquisition|school_readiness|learning|o:learning
52|school_community|Procure and distribute textbooks and classroom equipment|materials_availability||q;q;q
53|class|Distribute and actively use learning materials during lessons|teaching_practice||q;q;l
54|class|Develop localised and level-appropriate learning materials|materials_availability||l;l;l
55|class|Give learners choice and active control in learning|student_engagement||q;l;q
56|class|Use group work, paired reading, games and manipulatives|student_engagement||q;q
57|class|Facilitate pupil-led discussions and classroom talk|student_engagement||q;q;l
58|school_community|Train communities in school management;Support parent associations and school seed grants|community_participation|access|o:access;q
59|school_community|Have school committees design and use monitoring instruments|school_accountability||q;o:learning
60|class|Deliver universal classroom stress-reduction and prosocial sessions||wellbeing|q;q;l
61|class|Deliver structured drama, music, drawing, games and sport in groups;Train non-specialist activity facilitators||wellbeing|q;q;o:wellbeing;q
62|class|Screen children for elevated distress;Deliver creative-expressive and CBT-based classroom sessions||wellbeing|l;q;l;o:wellbeing
63|class|Train teachers in emotional communication and emotionally safe classrooms|supportive_classroom|wellbeing|q;q;o:wellbeing
64|child|Teach children to recognise their own emotions and cultural assets||wellbeing|q;o:wellbeing
65|child|Teach emotion regulation, coping and goal setting||wellbeing|q;o:wellbeing
66|child|Teach communication, cooperation and relationship-building||wellbeing|q;o:wellbeing
67|school_community|Train and coach school leaders in management and instructional leadership;Develop school improvement plans|school_management||q;q;q
68|school_community|Provide meals or snacks consumed at school||access;wellbeing|o:access;o:wellbeing;q
69|school_community|Distribute take-home food rations to households of enrolled children||access;wellbeing|q;o:access;q
70|school_community|Provide deworming, micronutrients or health education alongside feeding|| |o:wellbeing;q;q
71|school_community|Establish and support community-managed schools||access;learning|o:access;o:access;o:learning
72|class|Train teachers in subject-specific pedagogy through classroom practice|teaching_practice|learning|q;l
73|class|Have teachers rehearse and enact lessons during training|teaching_practice|learning|q;q
74|class|Record and review teaching videos with structured reflection|teaching_practice||q;l
75|class|Use messaging groups for teacher reminders and peer exchange|teacher_peer_learning||q;q;q
76|system|Link teacher professional development to career incentives|teacher_career_progression|learning|l;q
77|class|Teach structured lessons on gender norms and non-violence|gender_equitable_attitudes||q;r:gender_equitable_attitudes
78|school_community|Facilitate boys' and men's reflection on masculinity, gender and violence|gender_equitable_attitudes||q;r:gender_equitable_attitudes
79|school_community|Hold gender and education dialogue with parents and community gatekeepers|gender_equitable_attitudes||q;r:gender_equitable_attitudes
80|school_community|Build safe sex-separated toilets and handwashing facilities||access|q;l;o:access
81|school_community|Provide scholarships or transfers to girls||access|q;q;o:access
82|school_community|Provide girls' clubs, mentoring and safe spaces|girls_agency||q;q;r:girls_agency
83|class|Repeatedly assess learning levels and regroup learners|learning_level_identification||q;l;l
84|class|Group pupils by assessed learning level;Align instruction to each group's learning level|targeted_instruction||l;q;l
85|class|Prioritise a narrow set of foundational literacy and numeracy skills|targeted_instruction||q;q;l
86|school_community|Screen for trauma symptoms;Deliver manualised trauma-focused CBT components||wellbeing|l;l;l;l
87|school_community|Construct a chronological lifeline with a trained therapist;Revisit selected traumatic memories||wellbeing|l;q;l;o:wellbeing
88|school_community|Screen distressed youth;Deliver group interpersonal psychotherapy||wellbeing|q;l;l;o:wellbeing
89|school_community|Refer affected pupils to group counselling;Deliver school-based group psychosocial counselling||wellbeing|l;q;l;o:wellbeing
90|school_community|Provide individual counselling using trust and problem solving;Involve families in counselling||wellbeing|q;q;l;o:wellbeing
91|class|Train facilitators;Adapt content to local context;Provide sufficient delivery dosage|||q;l;q
92|school_community|Provide parenting education, counselling and mentoring|positive_parenting;caregiver_wellbeing||q;r:positive_parenting
93|school_community|Engage caregivers in structured family-strengthening activities|positive_parenting|wellbeing|r:positive_parenting;r:positive_parenting;o:wellbeing
94|school_community|Provide psychosocial support to displaced caregivers|caregiver_wellbeing||r:positive_parenting;r:caregiver_wellbeing
95|class|Maintain regular teacher contact and guidance in remote learning|||q
96|class|Exchange formative feedback between teachers and learners;Provide learner and caregiver feedback channels||learning;wellbeing|q;l
97|class|Organise facilitated remote peer learning groups||learning|q;q
98|school_community|Support caregivers to facilitate learning at home;Send regular caregiver reminders||learning|q;q
99|system|Combine synchronous and asynchronous remote learning modes;Offer internet and non-internet learning channels||access|q;q
100|class|Observe classroom instruction and give individualised coaching feedback|teaching_practice||q;q
101|class|Pair novice teachers with experienced mentors;Provide career and socialisation guidance|teacher_professional_support||q;q;q
102|class|Convene teacher learning circles and peer knowledge-sharing|teacher_peer_learning||q;q;q
103|class|Review recorded teaching with a remote coach;Provide iterative personalised feedback|teaching_practice||q;q;r:teaching_practice
104|class|Observe classroom instruction and give structured feedback|teaching_practice||q;l;q
105|class|Develop scripted or semi-scripted lesson plans|structured_pedagogy||q;q;l
106|class|Train teachers to deliver structured lesson plans|structured_pedagogy||q;q;l
107|class|Provide ongoing classroom supervision and feedback on structured lessons|structured_pedagogy||q;l;q
108|class|Provide teacher guides and pupil materials matched to structured lessons|structured_pedagogy||l;q;l
109|school_community|Pay households cash conditional on schooling behaviour||access|o:access;q;q
110|school_community|Pay households cash without schooling conditions||access|o:access;q;q
111|system|Monitor and enforce cash-transfer schooling conditions||access|q;o:access
112|school_community|Provide scholarships, fee subsidies or school vouchers||access|o:access;q;q
113|school_community|Combine cash transfers with education encouragement and community meetings||wellbeing|l;o:wellbeing
"""

RESULTS = {
    "fair_teacher_compensation": ("Fair and timely teacher compensation", "class"),
    "teacher_professional_recognition": ("Teacher professional recognition", "class"),
    "teacher_career_progression": ("Teacher career progression", "class"),
    "displaced_learner_inclusion": ("Inclusion of displaced learners in education provision", "system"),
    "student_engagement": ("Student engagement in learning", "class"),
    "teaching_practice": ("Teacher instructional practice", "class"),
    "service_access": ("Access to appropriate support and referral services", "school_community"),
    "school_accountability": ("School accountability", "school_community"),
    "belonging": ("Student identity and belonging", "school_community"),
    "intergroup_relations": ("Positive intergroup attitudes and relationships", "school_community"),
    "contextualised_content": ("Contextualised digital learning content", "class"),
    "teacher_inclusion_capacity": ("Teacher knowledge and capacity for inclusion", "class"),
    "inclusion": ("Inclusive school participation and environment", "school_community"),
    "teacher_wellbeing": ("Teacher wellbeing and manageable stress", "class"),
    "supportive_leadership": ("Supportive and participatory school leadership", "school_community"),
    "equity_monitoring": ("Identification of displacement-related equity gaps", "system"),
    "school_readiness": ("Readiness for and transition to school", "school_community"),
    "materials_availability": ("Availability of appropriate learning materials", "class"),
    "community_participation": ("Community participation in school management", "school_community"),
    "supportive_classroom": ("Emotionally supportive classroom climate", "class"),
    "school_management": ("School management and instructional leadership", "school_community"),
    "teacher_peer_learning": ("Teacher peer learning and exchange", "class"),
    "gender_equitable_attitudes": ("Gender-equitable and non-violent attitudes", "school_community"),
    "girls_agency": ("Girls' agency, aspirations and social connections", "school_community"),
    "learning_level_identification": ("Identification of current learning levels", "class"),
    "targeted_instruction": ("Instruction aligned to learners' levels", "class"),
    "positive_parenting": ("Positive parenting and caregiver efficacy", "school_community"),
    "caregiver_wellbeing": ("Caregiver wellbeing", "school_community"),
    "teacher_professional_support": ("Professional support for new teachers", "class"),
    "structured_pedagogy": ("Delivery of the structured pedagogy package", "class"),
}
OUTCOMES = {
    "access": "Child access to and participation in education",
    "learning": "Child learning",
    "wellbeing": "Child wellbeing and safety",
}

# Cross-driver/component links are included only where the cited definition
# explicitly describes the relevant relationship. They are not causal estimates.
CROSS = [
    (104, 100, 100, "C", "Observation and feedback form the coaching cycle."),
    (111, 109, 111, "C", "Monitoring and enforcement are design features of conditional transfers."),
    (83, 84, 83, "C", "Assessment assigns children to groups and supports regrouping."),
    (52, 53, 53, "C", "Materials must be available to be distributed and used in lessons."),
    (103, 100, 103, "C", "Remote coaching is an adaptation of the observation and feedback coaching cycle."),
]


def slug(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    fingerprint = hashlib.sha256(args.workbook.read_bytes()).hexdigest()
    if fingerprint != "919ba17854874dfcfa4c28ad4d016b7afbf97c34b90c5f36386519ef62f315c2":
        raise ValueError("This curation applies only to the original source workbook; its SHA-256 does not match.")
    args.output.mkdir(parents=True, exist_ok=True)
    workbook = openpyxl.load_workbook(args.workbook)
    menu = workbook["full menu"]
    colours = {"child": "#FC4C02", "class": "#007f79", "school_community": "#7e5aa6",
               "system": "#F6B0BD", "macro": "#8dd3b5", "none": "#999999"}
    shapes = {"outcome": "circle", "result": "triangle", "driver": "square",
              "activity": "diamond", "out_ind": "pentagon", "qual_ind": "hexagon",
              "quant_ind": "septagon"}
    nodes = {}
    edges = {}
    item_nodes = {}
    covered_rows = set()

    def node(name, level, category, description):
        identifier = category + "_" + slug(name)
        if not slug(name):
            raise ValueError(f"Empty identifier for {name!r}")
        candidate = {"id": identifier, "name": name, "level": level, "category": category,
                     "description": description, "colour": colours[level], "shape": shapes[category]}
        if identifier in nodes:
            previous = nodes[identifier]
            if (previous["name"], previous["level"], previous["category"]) != (name, level, category):
                raise ValueError(f"Node collision: {previous!r} / {candidate!r}")
        else:
            nodes[identifier] = candidate
        return identifier

    def result(key):
        name, level = RESULTS[key]
        return node(name, level, "result", name)

    def outcome(key):
        name = OUTCOMES[key]
        return node(name, "child", "outcome", name)

    def edge(source, target, kind, row, column, basis, citation=None):
        citation = citation or menu[f"E{row}"].value
        if not citation:
            raise ValueError(f"Missing primary source in row {row}")
        reference = f"{citation} [full menu!{column}{row}]"
        key = (source, target, kind)
        if source == target:
            raise ValueError(f"Self-link: {key}")
        if key not in edges:
            edges[key] = {"source": source, "target": target, "references": set(),
                          "direction": "Positive" if kind == "supports" else "",
                          "confidence": "", "symbol": "", "notes": "", "reviewed_by": "",
                          "last_updated": "", "colour": "#2f8a63" if kind == "supports" else "",
                          "id": f"{source}__{target}__{kind}", "type": kind, "evidence_basis": set()}
        edges[key]["references"].add(reference)
        edges[key]["evidence_basis"].add(basis)

    for line in ROWS.strip().splitlines():
        number, level, activities, results, outcomes, indicator_codes = line.split("|")
        row = int(number)
        if row in covered_rows or not menu[f"A{row}"].value:
            raise ValueError(f"Invalid or duplicate row {row}")
        covered_rows.add(row)
        name = menu[f"A{row}"].value.strip()
        description = menu[f"C{row}"].value.strip()
        # These four rows are explicitly described as outcome/mechanism rather
        # than independent interventions in the menu's interpretation column.
        category = "result" if row in {28, 64, 65, 66} else "driver"
        if row == 28:
            item = result("belonging")
            nodes[item]["description"] = f"{name}: {description}"
        else:
            item = node(name, level, category, description)
        item_nodes[row] = item
        for activity in filter(None, (x.strip() for x in activities.split(";"))):
            act = node(activity, level, "activity", activity)
            edge(act, item, "supports", row, "C", "Menu-described component; not an effect estimate.")
        for key in filter(None, (x.strip() for x in results.split(";"))):
            edge(item, result(key), "supports", row, "C",
                 "Menu-described mechanism, goal or finding; not necessarily an independently estimated effect.")
        for key in filter(None, (x.strip() for x in outcomes.split(";"))):
            edge(item, outcome(key), "supports", row, "C",
                 "Menu-described goal or finding; not necessarily an independently estimated effect.")

        indicators = [v.strip().rstrip(".") for v in menu[f"D{row}"].value.split(";")]
        codes = [v.strip() for v in indicator_codes.split(";")]
        if len(indicators) != len(codes):
            raise ValueError(f"Row {row}: {len(indicators)} indicators but {len(codes)} classifications: {indicators!r}")
        for text, code in zip(indicators, codes):
            # Pooled estimates are evidence values, not separate measures.
            # Keep their source cells on the relationship instead.
            text = re.sub(r" \(pooled odds ratio [^)]*\)$", "", text)
            if code == "q":
                indicator, target = "quant_ind", item
            elif code == "l":
                indicator, target = "qual_ind", item
            elif code.startswith("r:"):
                indicator, target = "out_ind", result(code[2:])
            elif code.startswith("o:"):
                indicator, target = "out_ind", outcome(code[2:])
            else:
                raise ValueError(f"Invalid indicator code: {row} {code}")
            # Implementation metrics with generic names (e.g. "teachers
            # trained") are different measures for different interventions.
            indicator_name = f"{text} [{nodes[target]['name']}]" if code in {"q", "l"} else text
            ind = node(indicator_name, nodes[target]["level"], indicator, text)
            edge(ind, target, "indicator", row, "D",
                 "Illustrative measure listed in the menu; not evidence of an observed change.")

    for source_row, target_row, evidence_row, column, basis in CROSS:
        edge(item_nodes[source_row], item_nodes[target_row], "supports",
             evidence_row, column, basis + " Association or component relationship, not an isolated effect.")

    # These citations come from the review narrative in column F rather than
    # the definition's primary-source column. Package effects are not
    # attributed to isolated components.
    narrative_links = [
        (item_nodes[12], outcome("learning"), 12, "Kwok, Sable and Smiley (2026)",
         "PlayMatters programme evidence reports learning gains; not an isolated play component effect."),
        (item_nodes[12], outcome("wellbeing"), 12, "Kwok, Sable and Smiley (2026)",
         "PlayMatters programme evidence reports wellbeing effects, with variation by setting."),
        (item_nodes[15], outcome("wellbeing"), 15, "Bick et al. (2025)",
         "WASH studies report selected health benefits; attendance and education effects are heterogeneous."),
        (item_nodes[16], outcome("wellbeing"), 16, "Bick et al. (2025)",
         "WASH studies report improved hygiene behaviours and selected health outcomes, with heterogeneous effects."),
        (item_nodes[28], result("student_engagement"), 28, "Aleghfeli et al. (2025)",
         "The narrative describes belonging as a condition for sustained educational engagement."),
        (item_nodes[30], outcome("learning"), 30, "Barnes and Katrin (2025)",
         "Digital programme gains are conditional on contextual design and support; not an isolated co-design effect."),
        (item_nodes[31], outcome("learning"), 31, "Barnes and Katrin (2025)",
         "Digital applications reported varied learning outcomes; effects depend on implementation."),
        (item_nodes[21], result("teaching_practice"), 21, "Kagan and Fabbri (2026)",
         "EmpaTeach improved positive practices but did not reduce teachers' use of violence."),
        (result("supportive_leadership"), outcome("learning"), 67, "Falk et al. (2019)",
         "The review describes school climate and leadership as shaping sustained learning."),
        (item_nodes[67], outcome("learning"), 67, "Anand et al. (2023)",
         "School leadership interventions showed a small average learning benefit, with implementation constraints."),
        (item_nodes[95], outcome("learning"), 95, "Pacitto et al. (2026)",
         "Teacher presence was associated with stronger remote outcomes; facilitated SMS maths is an illustrative programme."),
        (item_nodes[97], item_nodes[33], 95, "Pacitto et al. (2026)",
         "Facilitated groups improved the effectiveness of radio-based learning in a reported example."),
        (item_nodes[91], item_nodes[30], 91, "Barnes and Katrin (2025)",
         "Digital programme effectiveness depended on contextual design, integration and human support."),
        (result("targeted_instruction"), outcome("learning"), 83, "Pherali and Rinehart (2026)",
         "A catch-up programme using Teaching at the Right Level reported literacy gains; not an isolated component effect."),
        (result("structured_pedagogy"), outcome("learning"), 105, "Snilstveit et al. (2015)",
         "Evidence is for the combined structured pedagogy package, not each component separately."),
        (item_nodes[100], outcome("learning"), 100, "Kraft, Blazar and Hogan (2018)",
         "The coaching meta-analysis reports a learning gain; this does not establish a separate component effect."),
        (result("teaching_practice"), outcome("learning"), 100, "Kraft, Blazar and Hogan (2018)",
         "Coaching improved both instructional practice and learning; the intermediate causal pathway was not isolated."),
    ]
    for source, target, row, citation, basis in narrative_links:
        edge(source, target, "supports", row, "F", basis, citation)

    expected = {r for r in range(5, menu.max_row + 1) if menu[f"A{r}"].value}
    if covered_rows != expected:
        raise ValueError(f"Menu coverage differs: missing={expected-covered_rows}, extra={covered_rows-expected}")

    node_fields = ["id", "name", "level", "category", "description", "colour", "shape"]
    edge_fields = ["source", "target", "references", "direction", "confidence", "symbol",
                   "notes", "reviewed_by", "last_updated", "colour", "id", "type", "evidence_basis"]
    output_edges = []
    for data in edges.values():
        record = dict(data)
        record["references"] = "; ".join(sorted(record["references"]))
        record["evidence_basis"] = " | ".join(sorted(record["evidence_basis"]))
        output_edges.append(record)
    for filename, fields, records in [
        ("nodes.csv", node_fields, nodes.values()),
        ("relationships.csv", edge_fields, output_edges),
    ]:
        with (args.output / filename).open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)

    for sheet_name, fields, records in [
        ("Nodes", node_fields, nodes.values()),
        ("Relationships", edge_fields, output_edges),
    ]:
        sheet = workbook[sheet_name]
        if sheet.max_row > 1:
            sheet.delete_rows(2, sheet.max_row - 1)
        for col, field in enumerate(fields, 1):
            sheet.cell(1, col, field)
        for record in records:
            sheet.append([record[field] for field in fields])
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
    workbook.save(args.output / "driver_graph.xlsx")

    # Validate what was written, rather than only the in-memory construction.
    with (args.output / "nodes.csv").open(newline="", encoding="utf-8-sig") as f:
        saved_nodes = list(csv.DictReader(f))
    with (args.output / "relationships.csv").open(newline="", encoding="utf-8-sig") as f:
        saved_edges = list(csv.DictReader(f))
    ids = {n["id"] for n in saved_nodes}
    if len(ids) != len(saved_nodes):
        raise ValueError("Duplicate node IDs")
    names = [(slug(n["name"]), n["category"]) for n in saved_nodes]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate normalised names within a category")
    triples = [(e["source"], e["target"], e["type"]) for e in saved_edges]
    if len(set(triples)) != len(triples) or len({e["id"] for e in saved_edges}) != len(saved_edges):
        raise ValueError("Duplicate relationships")
    linked = set()
    adjacency = defaultdict(set)
    for e in saved_edges:
        if e["source"] not in ids or e["target"] not in ids:
            raise ValueError(f"Dangling endpoint: {e}")
        if not e["references"] or not e["evidence_basis"]:
            raise ValueError(f"Missing source or evidence basis: {e}")
        source_category = nodes[e["source"]]["category"]
        target_category = nodes[e["target"]]["category"]
        if e["type"] == "indicator":
            if source_category not in {"out_ind", "qual_ind", "quant_ind"} or target_category not in {"driver", "result", "outcome"}:
                raise ValueError(f"Invalid indicator relationship: {e}")
        elif e["type"] == "supports":
            if source_category not in {"activity", "driver", "result"} or target_category not in {"driver", "result", "outcome"}:
                raise ValueError(f"Invalid supports relationship: {e}")
        else:
            raise ValueError(f"Unknown relationship type: {e}")
        for ref in e["references"].split("; "):
            # Citations themselves can contain semicolons, so validate the
            # complete field by its source-cell markers below instead.
            if not ref.strip():
                raise ValueError(f"Empty reference: {e}")
        markers = re.findall(r"\[full menu!([CDF])(\d+)\]", e["references"])
        if not markers:
            raise ValueError(f"Missing menu cell reference: {e}")
        for column, number in markers:
            n = int(number)
            if not menu[f"{column}{n}"].value or not menu[f"E{n}"].value:
                raise ValueError(f"Invalid source cell: {e}")
            if column == "F":
                citations = [c for source, target, r, c, _ in narrative_links
                             if source == e["source"] and target == e["target"] and r == n]
                if not citations or any(c not in menu[f"F{n}"].value for c in citations):
                    raise ValueError(f"Narrative citation not found in source cell: {e}")
            elif f"{menu[f'E{n}'].value} [full menu!{column}{n}]" not in e["references"]:
                raise ValueError(f"Source citation does not match menu: {e}")
        linked.update((e["source"], e["target"]))
        if e["type"] == "supports":
            adjacency[e["source"]].add(e["target"])
    if linked != ids:
        raise ValueError(f"Unconnected nodes: {ids-linked}")

    def reaches_outcome(start):
        seen, queue = {start}, deque([start])
        while queue:
            current = queue.popleft()
            if nodes[current]["category"] == "outcome":
                return True
            for nxt in adjacency[current] - seen:
                seen.add(nxt)
                queue.append(nxt)
        return False

    no_path = [(r, menu[f"A{r}"].value) for r in sorted(expected)
               if not reaches_outcome(item_nodes[r])]
    reopened = openpyxl.load_workbook(args.output / "driver_graph.xlsx", read_only=True)
    if reopened["Nodes"].max_row != len(saved_nodes) + 1 or reopened["Relationships"].max_row != len(saved_edges) + 1:
        raise ValueError("Workbook and CSV row counts disagree")
    for sheet_name, fields, records in [
        ("Nodes", node_fields, saved_nodes), ("Relationships", edge_fields, saved_edges)
    ]:
        rows = reopened[sheet_name].iter_rows(values_only=True)
        if list(next(rows))[:len(fields)] != fields:
            raise ValueError(f"Workbook header differs: {sheet_name}")
        for row, record in zip(rows, records, strict=True):
            if [value if value is not None else "" for value in row[:len(fields)]] != [record[field] for field in fields]:
                raise ValueError(f"Workbook and CSV content differ: {sheet_name}")
    near_duplicates = []
    for i, first in enumerate(saved_nodes):
        for second in saved_nodes[i + 1:]:
            if first["category"] != second["category"]:
                continue
            ratio = difflib.SequenceMatcher(None, first["name"].lower(), second["name"].lower()).ratio()
            if ratio >= 0.9:
                near_duplicates.append((first["name"], second["name"]))
    counts = Counter(n["category"] for n in saved_nodes)
    report = [
        "GRAPH VALIDATION",
        f"Source workbook SHA-256: {fingerprint}",
        f"Menu rows represented: {len(covered_rows)} of {len(expected)}",
        f"Nodes: {len(saved_nodes)}; relationships: {len(saved_edges)}",
        "Node categories: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        f"Relationship types: {dict(Counter(e['type'] for e in saved_edges))}",
        "PASS: unique node IDs and normalised names within category.",
        "PASS: unique source/target/type triples and relationship IDs.",
        "PASS: every relationship endpoint exists; every node has at least one relationship.",
        "PASS: every relationship cites its menu source and an existing specific source cell.",
        "PASS: workbook sheets reopen and match the CSVs cell-for-cell.",
        "",
        "INTERPRETATION AND LIMITATIONS",
        "Evidence references are the menu's citations, not independently checked full-text studies.",
        "A supports edge means the menu describes a component, intended contribution, mechanism or finding.",
        "It does not establish a causal effect. Confidence and symbol are blank because inherited",
        "review-level strength cannot be assigned to individual links. Indicator links have no sign.",
        "No country or measurement-tool nodes are included.",
        "Implementation indicators are scoped to their target to avoid conflating e.g. teachers trained in different programmes.",
        "Result-to-outcome links are not invented where the menu does not state a direct pathway.",
        f"Menu items without a directed supports path to a child outcome: {len(no_path)}.",
        "These remain connected to their components, indicators or intermediate results and require review:",
    ]
    report.extend(f"  row {r}: {name}" for r, name in no_path)
    report.extend([
        "",
        "Duplicate checks compare IDs, normalised names within a category, and relationship triples.",
        f"Near-duplicate label candidates (same category, text similarity >= 0.90): {len(near_duplicates)}.",
        "These require semantic review; differently worded duplicates may also exist.",
        "The evidence and node classifications are curated interpretations and need substantive review.",
        "To regenerate: install openpyxl, then run python build_graph.py ORIGINAL_WORKBOOK.xlsx OUTPUT_DIRECTORY.",
        "The script checks the exact source workbook fingerprint before applying the row-specific curation.",
    ])
    report.extend(f"  {first} | {second}" for first, second in near_duplicates)
    (args.output / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
