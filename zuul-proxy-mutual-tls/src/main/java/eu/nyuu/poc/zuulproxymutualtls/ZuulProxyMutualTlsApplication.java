package eu.nyuu.poc.zuulproxymutualtls;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.zuul.EnableZuulProxy;

@EnableZuulProxy
@SpringBootApplication
public class ZuulProxyMutualTlsApplication {

    public static void main(String[] args) {
        SpringApplication.run(ZuulProxyMutualTlsApplication.class, args);
    }
}
