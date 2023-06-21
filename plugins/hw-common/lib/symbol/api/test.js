"use strict";
const { log } = require("console");
function Person(firstName, lastName) {
    this.firstName = firstName;
    this.lastName = lastName;
}
Person.prototype.printFullName = function () {
    log(`The Full name: ${this.firstName} ${this.lastName}`);
};
const person = new Person('kathir', 'vel');
person.printFullName();
log(person);
const abcd = 'firstName';
const human = {
    [abcd]: 'adsfsadf',
    lastName: 'k',
    printFullName: function () {
        log(`Full name : ${this.firstName} ${this.lastName}`);
    }
};
human.printFullName();
log(human);
