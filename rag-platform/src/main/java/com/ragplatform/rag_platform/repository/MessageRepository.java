package com.ragplatform.rag_platform.repository;

import com.ragplatform.rag_platform.model.Message;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface MessageRepository extends MongoRepository<Message, String> {

    List<Message> findByChatIdOrderByCreatedAtAsc(String chatId);


}