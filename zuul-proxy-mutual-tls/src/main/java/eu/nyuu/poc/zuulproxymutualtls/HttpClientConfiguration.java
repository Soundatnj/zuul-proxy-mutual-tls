package eu.nyuu.poc.zuulproxymutualtls;

import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.conn.ssl.TrustSelfSignedStrategy;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.PrivateKeyStrategy;
import org.apache.http.ssl.SSLContexts;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import java.io.File;

@Configuration
public class HttpClientConfiguration {

    @Value("${system.keystorePath}")
    private String keystorePath;

    @Bean
    public CloseableHttpClient httpClient() throws Exception {
        Resource resource = new FileSystemResource(keystorePath);

        File trustStoreFile = resource.getFile();

        SSLContext sslcontext = SSLContexts.custom()
                .loadTrustMaterial(trustStoreFile, "password".toCharArray(),
                        new TrustSelfSignedStrategy())
                .loadKeyMaterial(trustStoreFile, "password".toCharArray(),
                        "password".toCharArray())
                .build();

        // Allow all FQDN verifier, for tests
//        HostnameVerifier iDontCare = new HostnameVerifier() {
//            public boolean verify(String s, SSLSession sslSession) {
//                return true;
//            }
//        };

        // Allow TLSv12 protocol only
        SSLConnectionSocketFactory sslsf = new SSLConnectionSocketFactory(
                sslcontext,
                new String[]{"TLSv1.2"},
                null,
                SSLConnectionSocketFactory.getDefaultHostnameVerifier());

        return HttpClients.custom()
                .setSSLSocketFactory(sslsf)
                .build();
    }

}
