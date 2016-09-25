# Chalk 1.4
Simple, easy to learn interpreted programming language.
### Hello world!
`write "Hello world!"`
### Variables
Chalk supports integers, strings and boolean data types.
```
github = "dhill0n"
age = 15
likes_coding = true
has_gf = false
```

### If statements
Compare two values or variables and execute some code if they do or don't match
```
animal = "Cat"
favorite_animal = "Cat"
if @animal == @favorite_animal then
  write "You like cats too huh?"
end if`
```

### For loops
Repeat blocks of code as many times as you want
```
for x in 0 .. 10 {
  write @x
}
```

### While Loops
Repeat blocks of code while a condition is or isn't met
```
-- Will never ever be false! :D
while @likes_coding == true {
  write "Coding is amazing!"
}
```

### Functions
Group blocks of code for easy access and less repetition.
```
func greet (user) {
  write "Hello @user"
}

greet ("@github")
```
