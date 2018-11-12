# Mutual TLS with Spring Boot

## Starting webserver

This starts a basic HTTP server configured as you ask it, in this case HTTPS on the 443/tcp port with:

  * a server certificate signed by a CA dedicated to server certs, along with its key ;
  * a client certificate authority, making it refuse any connection not passing a client certificate signed by it.

```bash
sudo python2 ./webserver.py --ssl --port 443 --key CAs/server/server.xip.io.key --cert CAs/server/server.xip.io.crt --clientcerts CAs/client/ca.pem
```

## Testing it

```bash
cd CAs

curl -k --cert client/client.xip.io.crt --key client/client.xip.io.key https://127.0.0.1.xip.io
```

It should return a listing of the files inside the repo.

## Starting Spring Boot App

```bash
cd zuul-proxy-mutual-tls

mvn spring-boot:run
```

The app is configured to forward /hello/** from localhost:8080 to our webserver configured with mutual TLS.

It uses the keystore at `$REPO/keystores/client.jks` 
configured like the following:

  * Certificate and key of the client as .p12 file converted to .jks like this:

```bash
cd keystores

keytool -importkeystore -srckeystore ../CAs/client/client.xip.io.p12 -srcstoretype PKCS12 -destkeystore client.jks -deststoretype JKS
```

  * CA of the server imported as 'root' using the following command:
```bash
cd keystores

keytool -import -trustcacerts -alias root -file ../CAs/server/ca.pem -keystore client.jks
```
