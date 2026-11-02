package com.ragplatform.rag_platform.service;

import com.ragplatform.rag_platform.model.User;
import com.ragplatform.rag_platform.model.VerificationToken;
import com.ragplatform.rag_platform.repository.VerificationTokenRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class VerificationService {

    private final VerificationTokenRepository tokenRepository;
    private final EmailService emailService;

    public VerificationService(VerificationTokenRepository tokenRepository,
                               EmailService emailService) {

        this.tokenRepository = tokenRepository;
        this.emailService = emailService;
    }

    public void createVerificationToken(User user) {

        String token = UUID.randomUUID().toString();

        VerificationToken verificationToken = new VerificationToken();
        verificationToken.setUserId(user.getId());
        verificationToken.setToken(token);
        verificationToken.setCreatedAt(LocalDateTime.now());

        tokenRepository.save(verificationToken);

        String verificationLink =
                "http://localhost:8080/auth/verify?token=" + token;

        emailService.sendVerificationEmail(
                user.getEmail(),
                verificationLink
        );
    }
}