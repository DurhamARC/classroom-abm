extensions [ csv pathdir time ]

; data important from the PIPS project
breed [teachers teacher]  ; One type ofperson teachers
Breed [ students student] ; another type is students
Students-own [id inattentiveness hyper_impulsive start_maths end_maths ability deprivation]
Globals [
  Teach-control Teach-quality
  Current Current_class_id Chosen_class Number_of_classes
  Input_file Output_file Class_list Students_by_class
  Total_ticks Ticks_per_day Ticks_per_school_day Holiday_week_numbers
  Current_week Current_day Current_day_of_week Is_school_time
  School_learn_factor Home_learn_factor
]


to-report truncate-input-file
  ifelse length Input_file > 35 [
    report (word (substring Input_file 0 13) "..." (substring Input_file (length Input_file - 20) (length Input_file)))
  ][
    report Input_file
  ]
end

to initial-setup
  clear-all

  set-default-shape turtles "person" ; person shaped tutles

  set School_learn_factor 0.27
  set Home_learn_factor 0.5
end

to finish-setup

  read-data

  ask students [set end_maths start_maths]

  create-output-file

  calculate-holidays

end

to setup-ui ; for use in user interface

  initial-setup

  set Input_file user-file
  if Input_file != false [
    read-patches-from-csv
    reset-all

    set Chosen_class user-one-of "Select a class" fput "All" sort Class_list
    ifelse (Chosen_class = "All")[
      set Number_of_classes length Class_list
      set Current 0
      set Current_class_id item Current Class_list
    ] [
      set Number_of_classes 1
      set Current_class_id Chosen_class
      set Current position Chosen_class Class_list
    ]

    finish-setup
  ]

end

to setup-experiment ; for use in BehaviorSpace
  ; Save vars set by experiment before initial-setup calls reset-all
  let tmp_vars (list Input_file Chosen_class Random_select Number_of_holidays Weeks_per_holiday Number_of_groups Group_by School_learn_factor Home_learn_factor)
  initial-setup

  set Input_file item 0 tmp_vars
  set Chosen_class item 1 tmp_vars
  set Random_select item 2 tmp_vars
  set Number_of_holidays item 3 tmp_vars
  set Weeks_per_holiday item 4 tmp_vars
  set Number_of_groups item 5 tmp_vars
  set Group_by item 6 tmp_vars
  set School_learn_factor item 7 tmp_vars
  set Home_learn_factor item 8 tmp_vars

  read-patches-from-csv

  reset-all

  ifelse (Chosen_class = "All")[
    set Number_of_classes length Class_list
    set Current 0
    set Current_class_id item Current Class_list
  ] [
    if not member? Chosen_class Class_list [
      user-message (word "Invalid class " Chosen_class)
      stop
    ]
    set Number_of_classes 1
    set Current_class_id Chosen_class
    set Current position Chosen_class Class_list
  ]

  finish-setup

end

to reset-all ; But make sure not to call clear-all, as this also clears the global Class_list

  file-close-all ; Close any files open from last run
  clear-turtles
  ask patches [set pcolor black]

  ; Focus on maths and start with the maths levels on starting school

  ; changemean to 4 and sd to 1.4 Then 4, 1.0, The  4.0 0.8: changing the SD does not seem to make a difference except to incresase the correlation with start maths
  set Teach-quality  (random-normal 3.5  1.5)
  ; make sure quality does not go below 1
  ;if (Teach-quality < 1) [set Teach-quality 1]
  ; put a limit on quality
  ;if (Teach-quality > 5) [set Teach-quality 5]
  set Teach-control  (random-normal 3.5  1.1)
  ; make sure control does not go below 1
  ;if (Teach-control < 1) [set Teach-control 1]
  ; put a limit on control
  ;if (Teach-control > 5) [set Teach-control 5]

  reset-ticks

end

; procedure to read some turtle properties from a file
to read-patches-from-csv

  Set Current 0 ; This is the counter for the current class

  set Students_by_class []
  set Class_list []
  let current_class_students []
  let current_class 0
  let prev_class -1

  foreach csv:from-file Input_file [
    row ->

    if reduce and (map is-number? row) [ ; only parse rows that contain only numbers
      set current_class item 2 row
      if prev_class = -1 [
        set Class_list lput current_class Class_list
        set prev_class current_class
      ]

      if current_class != prev_class [
        set Class_list lput current_class Class_list
        set Students_by_class lput current_class_students Students_by_class
        set prev_class current_class
        set current_class_students []
      ]

      set current_class_students lput row current_class_students
    ]
  ]

  set Students_by_class lput current_class_students Students_by_class
end

to read-data ;Load current class

  set Current_class_id item Current Class_list
  let current_class_students item Current Students_by_class

  ; Determine how to space students into groups
  let n_students length current_class_students
  let max_students_per_group ceiling (n_students / Number_of_groups)
  let remainder_students_per_group n_students mod Number_of_groups
  let max_cols_per_group ceiling sqrt max_students_per_group
  let max_rows_per_group ceiling (max_students_per_group / max_cols_per_group)

  ; Have more columns than rows when it comes to groups
  let n_group_cols ceiling sqrt Number_of_groups
  let n_group_rows ceiling (Number_of_groups / n_group_cols)

  let n_rows n_group_rows * max_rows_per_group + n_group_rows - 1
  let n_cols n_group_cols * max_cols_per_group + n_group_cols - 1

  resize-world 0 (n_cols - 1) 0 (n_rows - 1)

  let s_count 0
  let x 0
  let y 0
  let current_group 0
  let students_in_group 0
  let group_x 0
  let group_y 0
  let rows_per_group max_rows_per_group
  let cols_per_group max_cols_per_group

  ; Sort students by ability or at random
  let sorted_students current_class_students
  ifelse Group_by = "Ability" [
    set sorted_students sort-by [ [s1 s2] -> item 4 s1 < item 4 s2 ] current_class_students
  ] [
    set sorted_students shuffle current_class_students
  ]

  foreach sorted_students [
    s ->
      if students_in_group >= max_students_per_group or
         (remainder_students_per_group > 0 and current_group >= remainder_students_per_group and students_in_group >= max_students_per_group - 1) [
        ; current group is full so move on to the next one
        set current_group current_group + 1
        set students_in_group 0
        set group_x floor (current_group / n_group_rows)
        set group_y (current_group mod n_group_rows)

        if remainder_students_per_group > 0 and current_group >= remainder_students_per_group [
          set cols_per_group ceiling sqrt (max_students_per_group - 1)
          set rows_per_group ceiling ((max_students_per_group - 1) / cols_per_group)
        ]
      ]

      ; fill up group a column at a time, so that 'remainder' students are spread
      ; between rows
      set x (group_x * max_cols_per_group + group_x) + floor (students_in_group / rows_per_group)
      set y (group_y * max_rows_per_group + group_y) + (students_in_group mod rows_per_group)

      ; CSV order is: start_maths,student_id,class_id,N_in_class,ability,inattentiveness,hyper_impulsive
      ask patch x y [
        set pcolor yellow
        sprout-students 1 [
          set color black
          set start_maths item 0 s
          set id item 1 s
          set ability item 4 s
          set inattentiveness item 5 s
          set hyper_impulsive item 6 s
          set deprivation  item 7 s
        ]
      ]

      set s_count s_count + 1
      set students_in_group students_in_group + 1
  ]

end

To calculate-holidays
  ; Calculate total ticks including holidays
  set Ticks_per_day 660 ; 11 hours * 60 minutes
  set Ticks_per_school_day 330 ; 5.5 hours * 60 minutes
  let ticks_per_week ticks_per_day * 7
  let total_days 317 ; # days from 1st September to 15th July

  let holiday_weeks Number_of_holidays * Weeks_per_holiday
  let school_weeks (ceiling (total_days / 7)) - holiday_weeks
  if school_weeks < 0 [
    user-message "There are more holidays than school weeks. Please ensure total weeks of holiday are 45 or fewer."
    stop
  ]

  set Total_ticks Ticks_per_day * total_days

  ; Calculate which weeks should be holidays
  let number_of_terms Number_of_holidays + 1 ; we don't include summer holidays
  let min_weeks_per_term floor (school_weeks / number_of_terms)
  let remainder_weeks School_weeks mod number_of_terms

  let Weeks_per_term [] ; number of weeks in each term
  foreach range Number_of_terms [ n ->
    let term_weeks min_weeks_per_term
    if (n < remainder_weeks) [ set term_weeks term_weeks + 1 ]
    set Weeks_per_term lput term_weeks Weeks_per_term
  ]

  set Holiday_week_numbers [] ; weeks which are holidays
  set Current_week 0
  foreach (sublist Weeks_per_term 0 Number_of_holidays) [ i ->
    set current_week current_week + i
    foreach range Weeks_per_holiday [ j ->
      set holiday_week_numbers lput current_week holiday_week_numbers
      set current_week current_week + 1
    ]
  ]

  set Current_week 0
  set Current_day 0
  set Is_school_time True
end

To go ; needs adjustment of the random parameters
  carefully [ let t ticks ] [
    user-message "Please run Setup first"
    stop
  ]

  let Was_school_time Is_school_time
  set Is_school_time check-if-school-time

  if Is_school_time [
    if not Was_school_time [ ; new week, so reset student status
      ask students [
        ask patch-here [set pcolor yellow]
      ];
    ]

    ; start teaching and passive students switch to learning mode (green) if teaching is good and they are not too inattentive
    ;   If teaching is good  If attentiveness is good
    ask students [if  ((((Random Random_select) + 1) < Teach-quality) and ((Random Random_select) + 1) > inattentiveness and pcolor = yellow) [
      ask patch-here [set pcolor green]
    ]]
    ; change from attentive to  passive (yellow) at random but more likely if the teaching quality is low
    ask patches [if ((((Random Random_select) + 1) > Teach-quality) and pcolor = green ) [set pcolor yellow]]
    ; be distruptive (red) at random if already passive (yellow) more likely if control is low and hyper-impulsive is high (is the > sign right?
    ask students [if ((((Random Random_select) + 1) > Teach-control ) and Random Random_select > (hyper_impulsive + 1) and pcolor = yellow) [
      ask patch-here [set pcolor red]
    ]]
    ;  disruptive to passive if control is good at random
    ask patches [if (( ((Random Random_select) + 1) < Teach-control) and pcolor = red) [set pcolor yellow]]
    ;if patch is green change to yellow if 3 neighboiurs or more are red
    ask patches [if ((count neighbors with [pcolor = red] ) > 2  and pcolor = green)
      [set pcolor yellow]]
    ;if patch is yellow change to red if 6 neighbours or more are red
    ask patches [if ((count neighbors with [pcolor = red])  > 5  and pcolor = yellow)
      [set pcolor red]]
  ]
  ask students [learn]  ; learn
  tick

  ;stop the program after a year of taught minutes (3 terms 12 weeks in a term, 5.5 hours a week 60 mins in an hour approx)
  if (ticks >= Total_ticks) [

    export-results

    ifelse (Chosen_class = "All") and (Current < Number_of_classes - 1) ; if "all" case and we have not just processed the last file
      [
        reset-all

        set Current Current + 1 ; increment file counter

        read-data

        ask students [set end_maths start_maths]
      ]
      [stop] ; otherwise we're done
  ]
end

to export-results ; export current results

  ; export patches to csv
  file-open Output_file
  ask students [
    file-print csv:to-row (list id Current_class_id end_maths Teach-control Teach-quality start_maths ability inattentiveness)
  ]
  file-close

end

to create-output-file ; generate filename and create blank output file

  if (not pathdir:isDirectory? "classes_output")[
    pathdir:create "classes_output"
  ]

  let date time:create ""
  let filename (word "output" (time:show date "yyyy-MM-dd_HHmmss-") behaviorspace-run-number ".csv")
  let sep pathdir:get-separator
  set Output_file (word pathdir:get-CWD-path sep "classes_output" sep filename)

  file-open Output_file
  file-print csv:to-row (list "id" "class" "end_maths" "Teach-control" "Teach-quality" "start_maths" "ability" "inattentiveness" )
  file-close

end

to-report check-if-school-time
  let today_ticks ticks mod Ticks_per_day

  if (today_ticks mod Ticks_per_day = 0) [
    set Current_day floor (ticks / Ticks_per_day)
    set Current_day_of_week Current_day mod 7
    set Current_week floor (Current_day / 7)
  ]

  ifelse (Current_day_of_week > 4) [ ; weekend
    report False
  ] [
    ; check if in holidays
    ifelse (member? Current_week Holiday_week_numbers) [
      report False
    ] [
      ; it's a school day so check time of day
      ; for simplicity the first part of the day is school time, the rest not
      report today_ticks < Ticks_per_school_day
    ]
  ]

end

to learn
  ; learn final amount gives about the right average scores at the end
  ; by being

  ifelse Is_school_time [
    ; ability is zscore of factor weightted average of vocab, maths & reading
    ;  incrementing gain X 2 does not make a massive difference
    ; tried changing SD below from .1 to 0.08
    if (pcolor = green) [set end_maths end_maths + School_learn_factor * (((random-normal ((5 + ability) / 2000) .08) ) + ((random-normal (5 / 2000) .08) )  )] ;
    ; adjusted the above to include an increment which does not depend on ability just random
  ] [
    ; by getting older maths changes
    set end_maths end_maths + Home_learn_factor * (( (6 - deprivation) / 3) ^ .01) * (((random-normal ((5 + ability) / 2000) .08) ) + ((random-normal (5 / 2000) .08) ))
    ; ditto to adjustment
    ; add deprivation to a power to reduce its spread
    ; NB the last two rows of code have been adjusted by extensive trial and error on one class to give suitable growth overall and correlations between variables
    ; by getting older ability changes
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
273
67
642
334
-1
-1
51.8
1
10
1
1
1
0
0
0
1
0
6
0
4
1
1
1
ticks
1.0

BUTTON
16
16
125
49
Set up
setup-ui
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
133
16
242
49
Go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
16
400
125
445
Average maths
Mean [end_maths] of students
1
1
11

TEXTBOX
273
16
423
58
Yellow Passive\nGreen learning\nRed disruptive\n
11
0.0
1

SLIDER
16
305
242
338
Random_select
Random_select
5
6
5.0
1
1
NIL
HORIZONTAL

MONITOR
133
400
242
445
SD maths
Standard-deviation [end_maths] of students
2
1
11

MONITOR
16
347
125
392
Current class ID
Current_class_id
0
1
11

MONITOR
16
59
242
104
Input File
truncate-input-file
17
1
11

MONITOR
16
113
125
158
Chosen class
Chosen_class
17
1
11

INPUTBOX
16
237
125
297
Number_of_holidays
2.0
1
0
Number

INPUTBOX
133
237
242
297
Weeks_per_holiday
2.0
1
0
Number

INPUTBOX
16
168
125
228
Number_of_groups
4.0
1
0
Number

CHOOSER
133
168
242
213
Group_by
Group_by
"Ability" "Random"
0

@#$#@#$#@
## WHAT IS IT?

This a phenomenon-based model . Classrooms in school are places when students are supposed to learn and the most often do. But things can go awry; the students can play up and that can result in an unruly class and learning can suffer.  This model aims to look at how much students learn according to how good the teacher is a classroom control and how good he or she is at teaching per se.

## HOW IT WORKS

The  model sets out the students in each class in a user-specified number of groups. They can have one of three states: learning, passive and disruptive. The students start with a measured level of their  mathis from the PIPS porject. The teacher has two variables ; Control and Teaching. Each is measured on a five point scale from awful (1) to brilliant (5) and is generated at random from a normal distribution with mean 3.5.
During the teaching day the teacher teaches and the students occupy one of the three states. They can learn (green) and whilst learning their maths increments slightgly and by an amount which is moderated by the child's measured ability. At each time point there is a probability that they become passive (yellow) or disruptive (red). The probability is related to: a) the Teaching and Control variables b) data on the students inattentivess and hyperactivity/impulsiveness imported from the PIPS anonymised database.
A student’s state is also influenced by the state of the other students. Two or more disruptive neighbouring students ensure that a student cannot learn. Five or more disruptive neighbours means that that student wil be disruptive.


## HOW TO USE IT

Create an input CSV file with headings `start_maths,student_id,class_id,N_in_class,ability,inattentiveness,hyper_impulsive` (or use one of the sample files in **input_classes**).

Output CSVs will be generated with results for each student, and will be placed in the **output_files** directory.

### Interface Mode

Press **Set up**, and select your input file, then choose a class (or **All**). Set a value for **Random_select**, then press **Go**.

### BehaviorSpace Mode

In BehaviorSpace mode you can set and vary the following variables:

```
["Input_file" "classes_input/test_input_short.csv"]
["Chosen_class" "All"]
["Random_select" 5]
["Number_of_holidays" 2]
["Weeks_per_holiday" 2]
["Number_of_groups" 4]
["Group_by" "Ability" "Random"]

```

`Input_file` should be the path to the input file, either relative to this NetLogo file or as an absolute path.

`Chosen_class` can either be set to be `"All"` or a specific class id or set of class ids.

```
["Chosen_class" "All"]
```

will run the experiment for all classes in the input file. Each run will generate a single output file containing results for all classes.

```
["Chosen_class" 3971049 4741049]
```

will run the experiement for each of the two classes (as well as varying any other parameters used in BehaviorSpace). Each class will have its own runs in BehaviorSpace, so the output files will contain the results for one class only.

## THINGS TO NOTICE

Watch for learning in the class (patches go green) and for disruption (patches got red) Also note the amount of learning of the class (Average maths) shown in the box as well as the standard deviation of the class.

## THINGS TO TRY

Look for the difference that changing Control and Teach_Quality make

## EXTENDING THE MODEL

The individual studenst could be give characteristics such as their conscienciousness and propensity to disrupt.

At a more complex level 12 classes are run one after another with student data taken from PIPS with with the teacher Teaching and Control variable randomly chosen from a normal distribution.

## NETLOGO FEATURES

None

## Analysis

Using ANOVA

see Jamovi expt classroom v05

## RELATED MODELS

None

## CREDITS AND REFERENCES

None
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.1.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="experiment" repetitions="1" runMetricsEveryStep="false">
    <setup>setup-experiment</setup>
    <go>go</go>
    <exitCondition>Ticks_per_day = 0 or
Holiday_week_numbers = 0</exitCondition>
    <metric>Mean [start_maths] of students</metric>
    <metric>Mean [end_maths] of students</metric>
    <enumeratedValueSet variable="Input_file">
      <value value="&quot;classes_input/test_input_short.csv&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Chosen_class">
      <value value="&quot;All&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Random_select">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Number_of_holidays">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Weeks_per_holiday">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Number_of_groups">
      <value value="4"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Group_by">
      <value value="&quot;Ability&quot;"/>
      <value value="&quot;Random&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="School_learn_factor">
      <value value="0.27"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Home_learn_factor">
      <value value="0.5"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
