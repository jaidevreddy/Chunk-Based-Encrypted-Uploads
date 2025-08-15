#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/rand.h>
#include <openssl/err.h>

#define PORT 9100
#define AES_KEY_SIZE 32

void handle_client(int client_socket) {
    FILE *pub_fp = fopen("client_pub.pem", "wb");
    char buffer[2048];
    int len = recv(client_socket, buffer, sizeof(buffer), 0);
    fwrite(buffer, 1, len, pub_fp);
    fclose(pub_fp);
    printf("📥 Received and saved client's public key.\n");

    FILE *fp = fopen("client_pub.pem", "r");
    RSA *client_rsa = PEM_read_RSA_PUBKEY(fp, NULL, NULL, NULL);
    fclose(fp);

    unsigned char aes_key[AES_KEY_SIZE];
    RAND_bytes(aes_key, AES_KEY_SIZE);

    unsigned char encrypted[512];
    int encrypted_len = RSA_public_encrypt(AES_KEY_SIZE, aes_key, encrypted, client_rsa, RSA_PKCS1_OAEP_PADDING);

    send(client_socket, encrypted, encrypted_len, 0);
    printf("📤 Encrypted AES key sent to client.\n");

    FILE *aes_fp = fopen("aes_key.bin", "wb");
    fwrite(aes_key, 1, AES_KEY_SIZE, aes_fp);
    fclose(aes_fp);

    RSA_free(client_rsa);
    close(client_socket);
}

int main() {
    int server_socket, client_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_size = sizeof(client_addr);

    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr));
    listen(server_socket, 5);
    printf("🚀 Key Exchange Server listening on port %d...\n", PORT);

    while (1) {
        client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &addr_size);
        handle_client(client_socket);
    }

    close(server_socket);
    return 0;
}