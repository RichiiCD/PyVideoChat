# PyVideoChat

Advanced Python-based secure video chat room application using socket library. All the project is entirely developed using socket library for client/server connection and TLS for communication encryption. Run the local server, then open the client interface and logging with the username and the chat room ID.

## Who does it works?
The client encrypt and send frames from his camera, using the socket and TLS python libraries. Then, the server encrypts and sends the frame to all the members of the room. These clients receive the encrypted frame and decrypts it to show it in the interface.
