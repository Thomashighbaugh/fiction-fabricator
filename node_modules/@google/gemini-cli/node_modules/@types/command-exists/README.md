# Installation
> `npm install --save @types/command-exists`

# Summary
This package contains type definitions for command-exists (https://github.com/mathisonian/command-exists).

# Details
Files were exported from https://github.com/DefinitelyTyped/DefinitelyTyped/tree/master/types/command-exists.
## [index.d.ts](https://github.com/DefinitelyTyped/DefinitelyTyped/tree/master/types/command-exists/index.d.ts)
````ts
export = commandExists;

declare function commandExists(commandName: string): Promise<string>;
declare function commandExists(
    commandName: string,
    cb: (error: null, exists: boolean) => void,
): void;

declare namespace commandExists {
    function sync(commandName: string): boolean;
}

````

### Additional Details
 * Last updated: Mon, 06 Nov 2023 22:41:05 GMT
 * Dependencies: none

# Credits
These definitions were written by [BendingBender](https://github.com/BendingBender).
