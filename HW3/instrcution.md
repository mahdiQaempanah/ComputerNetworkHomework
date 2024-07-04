## Practical Exercise for Network Layer

In this exercise, you need to simulate routing using Distance Vector Routing.

Your task is to simulate a real-time router.

Your program reads the inputs line by line and, depending on the message, either updates its distance vector or performs packet routing.

In all parts of the question, assume that the input subnets do not overlap. For example, 1.2.3.4/24 and 1.2.2.1/16 will not appear together in the inputs.

### Types of Inputs

The types of program inputs are as follows:

- Adding a link
- Removing a link
- Distance vector of a neighbor
- Printing the distance vector
- Entering a new packet
- Exiting the program

#### Adding a Link

If a link is added to the router, a message with the following format is read:

```
add link <id> <neighbor-ip-address>/<subnet-mask-bits-number> <distance-estimate>
```

For example:

```
add link 2 1.2.3.4/24 12
```

#### Removing a Link

If a link goes down or is removed, a message with the following format is read:

```
remove link <id>
```

For example:

```
remove link 2
```

#### Updating the Distance Vector

If a neighbor sends its distance vector to this router, the following messages are received:

First, a message with the following format is read:

```
update <link-id> <distance-vector-length>
```

Then, in the next `distance-vector-length` lines, a distance vector entry is given in the following format:

```
<ip-address>/<subnet-mask-bits-number> <distance-estimate>
```

For example:

```
update 2 3
1.2.4.1/24 30
1.2.5.1/24 32
1.3.8.1/16 45
```

#### Printing the Distance Vector

If the following message is seen:

```
print
```

The device should print all its distance vector entries in ascending order of IP address in the following format:

```
<ip-address>/<subnet-mask-bits-number> <distance-estimate>
```

For example:

```
1.1.1.1/24 3
1.1.2.1/24 7
1.1.11.3/24 5
1.1.20.4/28 28
1.2.0.0/16 18
```

#### Entering a New Packet

If a packet enters the device, a message with the following format is read:

```
route <destination-ip-address>
```

And a message with the following format is written:

```
<link-id>
```

#### Exiting the Program

Upon entering the command:

```
exit
```

The program execution ends.

### Sample Input 1

```
add link 1 192.168.1.0/24 5
add link 2 192.168.2.0/24 10
print
route 192.168.1.15
route 192.168.2.20
remove link 1
print
route 192.168.1.15
exit
```

### Sample Output 1

```
192.168.1.0/24 5
192.168.2.0/24 10
1
2
192.168.2.0/24 10
No route found
```

### Sample Input 2

```
add link 1 192.168.1.0/24 5
add link 2 192.168.3.0/24 15
update 2 2
192.168.4.0/24 7
192.168.5.0/24 10
print
route 192.168.4.25
route 192.168.5.30
exit
```

### Sample Output 2

```
192.168.1.0/24 5
192.168.3.0/24 15
192.168.4.0/24 22
192.168.5.0/24 25
2
2
```