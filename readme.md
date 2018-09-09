# md_template v2.0
This time not so *hacky*...

## TODO
* [ ] compiling templates to *AST*
    - [x] tokenize
    - [ ] build AST
        * [x] TEXT
        * [x] STAT
        * [ ] ENV
    - maybe optimize AST
* [ ] apply compiled AST
    - [ ] walk AST & apply
        * [x] TEXT
        * [x] STAT
        * [ ] ENV
* [ ] find a way to put ASR into file
    - [ ] put AT into file
    - [ ] get it out again...