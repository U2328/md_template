# md_template v2.0
This time not so *hacky*...

## TODO
* [ ] compiling templates to *AST*
    - [x] tokenize
    - [x] build AST
        * [x] TEXT
        * [x] STAT
        * [x] ENV
    - [ ] optimize AST
* [x] apply compiled AST
    - [x] walk AST & apply
        * [x] TEXT
        * [x] STAT
        * [x] ENV
* [x] find a way to put ASR into file
    - [x] put AT into file
    - [x] get it out again...