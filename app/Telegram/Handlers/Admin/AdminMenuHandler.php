<?php

namespace App\Telegram\Handlers\Admin;

use App\Telegram\Guards;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class AdminMenuHandler
{
    public function handle(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        if (!Guards::requireAdmin($userId, $cbq->getId())) {
            return;
        }

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => '*Admin Panel*',
            'parse_mode'   => 'Markdown',
            'reply_markup' => json_encode(Keyboards::adminMenu()),
        ]);
    }
}
