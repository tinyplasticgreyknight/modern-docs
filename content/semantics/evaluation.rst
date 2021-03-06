Evaluation
==========

It has been mentioned that Modern Data's type system is dependent; that is, the type of a value that comes later on is allowed to depend upon the actual value of an earlier one. It is necessary for the infrastructure to know what these dependent types evaluate to, which means that there must be an evaluator - a means of actually executing the function that computes each dependent type and determining its results.

The evaluation algorithm is given here as two mutually-recursive functions, and is a part of this specification: Evaluation must always proceed in this fashion. This is because, in limited-memory scenarios, the workings of the algorithm are observable to clients of the library (though not to the evaluated functions), inasmuch as the evaluation and hence the requested operation can fail in the event of an out-of-memory condition, and the only way to predict whether sufficient memory is available is to understand the algorithm.

Given elsewhere in this specification are descriptions of the functions performed by every possible builtin node, and their "static arities". Loosely, the static arities are the number of parameters they take, but in the event of a function returning a function, the precise meaning of this becomes unclear. The meaning of the static arity is simply that it is a parameter of the algorithm below, and is no greater than the maximum number of parameters which the builtin can be successively applied to. A static arity of zero is permitted, and denotes a computed value returned immediately rather than a function (the algorithm below is still used to compute this).

Initially, a node is the only thing given and we invoke the first of the functions given below, using an empty target stack.

To evaluate a node, given a target stack:

#. If it is a backreference node with zero-based index N, return the Nth item from the end of the target stack. Proceed to step 2.
#. If it is an application node, return the result of applying its left field, with the target stack given and a parameter stack containing solely the right field. Otherwise, proceed to step 3.
#. Return the node unchanged.

To apply a node (also called the left node), given a target stack and a parameter stack:

#. Initialize the intermediate result to the left node, and the remaining-parameter stack to a copy of the parameter stack. Proceed to step 2.
#. If the intermediate result is a lambda node and the remaining-parameter stack is nonempty, go to step 8. Otherwise, proceed to step 3.
#. If the intermediate result is an apply node, go to step 9. Otherwise, proceed to step 4.
#. If the intermediate result is not a builtin node, go to step 6. Otherwise, proceed to step 5.
#. If the intermediate result, which is a builtin node, has static arity N, and there are at least N items on the parameter stack, go to step 10. Otherwise, proceed to step 6.
#. If the parameter stack is empty, return the intermediate result. Otherwise, proceed to step 7.
#. Pop a value from the remaining-parameter stack. Replace the intermediate result with an application node with the former value of the intermediate result as its left field, and the popped value as its right field. Go to step 6.
#. The intermediate result is a lambda node. Pop a node from the remaining-parameter stack; compute the result of evaluating it with the current target stack, and call this result the "right node". Construct a copy of the target stack. Onto this copy, push the right node. Compute the result of evaluating the left node, with the copied target stack. Replace the intermediate result with the result of this computation. Go to step 2.
#. The intermediate result is an apply node. Push the intermediate result onto the remaining-parameter stack. Replace the intermediate result with its left field. Go to step 2.
#. The intermediate result is a builtin node. Let the builtin be the function or computed value denoted by its value, and N be its static arity. Pop N nodes from the parameter stack, and perform the builtin on these parameters, giving them in order starting with the one which was at the end of the parameter stack. Replace the intermediate result with the node produced by performing the builtin. Go to step 2.
