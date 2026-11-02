package com.ragplatform.rag_platform.service;

import com.ragplatform.rag_platform.model.PasswordResetToken;
import com.ragplatform.rag_platform.model.User;
import com.ragplatform.rag_platform.repository.PasswordResetTokenRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class PasswordResetService {

    private final PasswordResetTokenRepository resetTokenRepository;
    private final EmailService emailService;

    public PasswordResetService(PasswordResetTokenRepository resetTokenRepository,
                                EmailService emailService) {

        this.resetTokenRepository = resetTokenRepository;
        this.emailService = emailService;
    }

    public void createPasswordResetToken(User user) {

        String token = UUID.randomUUID().toString();

        PasswordResetToken resetToken = new PasswordResetToken();
        resetToken.setUserId(user.getId());
        resetToken.setToken(token);
        resetToken.setCreatedAt(LocalDateTime.now());

        resetTokenRepository.save(resetToken);

        String resetLink =
                "http://localhost:5173/reset-password?token=" + token;

        emailService.sendVerificationEmail(
                user.getEmail(),
                "Reset your password:\n\n" + resetLink
        );
    }
}