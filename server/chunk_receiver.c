#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <sys/socket.h>
#include <fcntl.h>

#define PORT 9191
#define AES_KEY_FILE "aes_key.bin"
#define BUFFER_SIZE 8192

AES_KEY aesKey;

void decrypt_chunk(unsigned char *ciphertext, int ciphertext_len, unsigned char *output) {
    unsigned char iv[16];
    memcpy(iv, ciphertext, 16);  // Extract IV
    AES_KEY tempKey;
    AES_set_decrypt_key((const unsigned char *)aesKey.rd_key, 256, &tempKey);
    AES_cbc_encrypt(ciphertext + 16, output, ciphertext_len - 16, &tempKey, iv, AES_DECRYPT);
}

int recv_full(int sockfd, unsigned char *buf, int len) {
    int total = 0, n;
    while (total < len) {
        n = recv(sockfd, buf + total, len - total, 0);
        if (n <= 0) return n;
        total += n;
    }
    return total;
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};

    // Load AES key
    FILE *key_file = fopen(AES_KEY_FILE, "rb");
    if (!key_file) {
        perror("❌ Failed to open AES key file");
        return 1;
    }

    unsigned char key[32];  // 256-bit key
    fread(key, 1, 32, key_file);
    fclose(key_file);
    AES_set_decrypt_key(key, 256, &aesKey);

    // Socket setup
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("❌ socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    listen(server_fd, 5);
    printf("🚀 Chunk Upload Server running on port %d...\n", PORT);

    while (1) {
        client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) {
            perror("❌ accept");
            continue;
        }

        printf("\n👤 New client connected!\n");

        memset(buffer, 0, sizeof(buffer));
        recv(client_fd, buffer, 1024, 0);
        char *filename = strtok(buffer, "|");
        int total_chunks = atoi(strtok(NULL, "|"));
        send(client_fd, "OK", 2, 0);

        printf("📁 Receiving file: %s (%d chunks)\n", filename, total_chunks);

        char output_path[256];
        snprintf(output_path, sizeof(output_path), "received_%s", filename);
        FILE *out = fopen(output_path, "wb");

        for (int i = 0; i < total_chunks; i++) {
            unsigned char len_buf[4];
            if (recv_full(client_fd, len_buf, 4) <= 0) {
                fprintf(stderr, "❌ Failed to receive chunk length\n");
                break;
            }

            int chunk_len = (len_buf[0]<<24) | (len_buf[1]<<16) | (len_buf[2]<<8) | len_buf[3];
            if (chunk_len <= 16) {
                fprintf(stderr, "❌ Invalid chunk length: %d\n", chunk_len);
                break;
            }

            unsigned char *enc_chunk = malloc(chunk_len);
            if (!enc_chunk || recv_full(client_fd, enc_chunk, chunk_len) <= 0) {
                fprintf(stderr, "❌ Failed to receive chunk data\n");
                free(enc_chunk);
                break;
            }

            int decrypted_len = chunk_len - 16;
            unsigned char *dec_chunk = malloc(decrypted_len);
            if (!dec_chunk) {
                fprintf(stderr, "❌ Memory allocation failed for decrypted chunk\n");
                free(enc_chunk);
                break;
            }

            decrypt_chunk(enc_chunk, chunk_len, dec_chunk);
            fwrite(dec_chunk, 1, decrypted_len, out);

            free(enc_chunk);
            free(dec_chunk);

            printf("✅ Chunk %d/%d decrypted\n", i + 1, total_chunks);
        }

        fclose(out);
        close(client_fd);
        printf("📦 File saved: %s\n🔁 Waiting for next file...\n", output_path);
    }

    return 0;
}